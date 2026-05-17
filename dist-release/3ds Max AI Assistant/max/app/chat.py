import json
import urllib.error
import urllib.request

from .settings import MAX_RESPONSE_TOKENS, MCP_SERVER_URL, MODELS, SYSTEM_PROMPT


class ChatEngine:
    def __init__(self, mcp_client):
        self.mcp = mcp_client
        self.server_url = mcp_client.server_url
        self.histories = {
            "anthropic": [],
            "openai": [],
            "openrouter": [],
        }

    def reset(self, provider=None):
        if provider:
            self.histories[provider] = []
        else:
            for key in self.histories:
                self.histories[key] = []

    def send(self, text, provider, api_key, model=None, on_tool_call=None, on_usage=None):
        usage_total = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "calls": 0}

        def track_usage(usage):
            usage_total["input_tokens"] += usage["input_tokens"]
            usage_total["output_tokens"] += usage["output_tokens"]
            usage_total["total_tokens"] += usage["total_tokens"]
            usage_total["calls"] += 1
            if on_usage:
                on_usage(usage)

        if provider == "openai":
            reply = self._send_openai(text, api_key, model or MODELS["openai"], on_tool_call, track_usage)
        elif provider == "openrouter":
            reply = self._send_openrouter(text, api_key, model or MODELS["openrouter"], on_tool_call, track_usage)
        else:
            reply = self._send_anthropic(text, api_key, model or MODELS["anthropic"], on_tool_call, track_usage)

        if on_usage and usage_total["calls"]:
            on_usage({
                "provider": provider,
                "input_tokens": usage_total["input_tokens"],
                "output_tokens": usage_total["output_tokens"],
                "total_tokens": usage_total["total_tokens"],
                "calls": usage_total["calls"],
                "summary": True,
            })

        return reply

    def _send_anthropic(self, text, api_key, model, on_tool_call, on_usage):
        messages = self.histories["anthropic"]
        messages.append({"role": "user", "content": text})

        response = self._call_anthropic(messages, api_key, model)
        self._emit_usage("anthropic", response, on_usage)
        while response.get("stop_reason") == "tool_use":
            messages.append({"role": "assistant", "content": response.get("content", [])})
            tool_results = []

            for block in response.get("content", []):
                if block.get("type") != "tool_use":
                    continue

                name = block["name"]
                args = block.get("input", {})
                if on_tool_call:
                    on_tool_call(name, args)

                try:
                    result = self.mcp.call_tool(name, args)
                    result_text = result.get("content", [{}])[0].get("text", "OK")
                except Exception as exc:
                    result_text = f"Error: {exc}"

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": result_text,
                })

            messages.append({"role": "user", "content": tool_results})
            response = self._call_anthropic(messages, api_key, model)
            self._emit_usage("anthropic", response, on_usage)

        reply = "\n".join(
            block.get("text", "")
            for block in response.get("content", [])
            if block.get("type") == "text"
        )
        messages.append({"role": "assistant", "content": response.get("content", [])})
        return reply

    def _send_openai(self, text, api_key, model, on_tool_call, on_usage):
        messages = self.histories["openai"]
        messages.append({
            "role": "user",
            "content": [{"type": "input_text", "text": text}],
        })

        response = self._call_openai(messages, api_key, model)
        self._emit_usage("openai", response, on_usage)
        while True:
            output = response.get("output", [])
            messages.extend(output)
            tool_calls = [item for item in output if item.get("type") == "function_call"]
            if not tool_calls:
                break

            tool_outputs = []
            for tool_call in tool_calls:
                args = self._parse_tool_arguments(tool_call.get("arguments"))
                if on_tool_call:
                    on_tool_call(tool_call["name"], args)

                try:
                    result = self.mcp.call_tool(tool_call["name"], args)
                    result_text = result.get("content", [{}])[0].get("text", "OK")
                except Exception as exc:
                    result_text = f"Error: {exc}"

                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": tool_call["call_id"],
                    "output": result_text,
                })

            messages.extend(tool_outputs)
            response = self._call_openai(messages, api_key, model)
            self._emit_usage("openai", response, on_usage)

        return self._extract_openai_text(response)

    def _send_openrouter(self, text, api_key, model, on_tool_call, on_usage):
        messages = self.histories["openrouter"]
        messages.append({"role": "user", "content": text})

        response = self._call_openrouter(messages, api_key, model)
        self._emit_usage("openrouter", response, on_usage)
        while True:
            message = response.get("choices", [{}])[0].get("message", {})
            messages.append(message)
            tool_calls = message.get("tool_calls") or []
            if not tool_calls:
                break

            for tool_call in tool_calls:
                if tool_call.get("type") != "function":
                    continue

                function = tool_call.get("function", {})
                name = function.get("name")
                args = self._parse_tool_arguments(function.get("arguments"))
                if on_tool_call:
                    on_tool_call(name, args)

                try:
                    result = self.mcp.call_tool(name, args)
                    result_text = result.get("content", [{}])[0].get("text", "OK")
                except Exception as exc:
                    result_text = f"Error: {exc}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id"),
                    "content": result_text,
                })

            response = self._call_openrouter(messages, api_key, model)
            self._emit_usage("openrouter", response, on_usage)

        return response.get("choices", [{}])[0].get("message", {}).get("content", "")

    def _call_anthropic(self, messages, api_key, model):
        body = {
            "model": model,
            "max_tokens": MAX_RESPONSE_TOKENS,
            "system": SYSTEM_PROMPT,
            "messages": messages,
            "tools": self.mcp.anthropic_tools() or None,
        }
        return self._post_json("/llm/anthropic", body, api_key)

    def _call_openai(self, messages, api_key, model):
        body = {
            "model": model,
            "instructions": SYSTEM_PROMPT,
            "max_output_tokens": MAX_RESPONSE_TOKENS,
            "input": messages,
            "tools": self.mcp.openai_tools() or None,
        }
        return self._post_json("/llm/openai", body, api_key)

    def _call_openrouter(self, messages, api_key, model):
        tools = self.mcp.openai_chat_tools()
        body = {
            "model": model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            "max_tokens": MAX_RESPONSE_TOKENS,
        }
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        return self._post_json("/llm/openrouter", body, api_key)

    def _post_json(self, path, body, api_key):
        data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            f"{self.server_url}{path}",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "x-llm-api-key": api_key,
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM proxy error {exc.code}: {detail}")

    @staticmethod
    def _emit_usage(provider, response, on_usage):
        if not on_usage:
            return

        usage = response.get("usage") or {}
        if provider == "openrouter":
            input_tokens = usage.get("prompt_tokens")
            output_tokens = usage.get("completion_tokens")
        else:
            input_tokens = usage.get("input_tokens")
            output_tokens = usage.get("output_tokens")

        if input_tokens is None and output_tokens is None:
            return

        input_tokens = input_tokens or 0
        output_tokens = output_tokens or 0
        on_usage({
            "provider": provider,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": usage.get("total_tokens", input_tokens + output_tokens),
        })

    @staticmethod
    def _parse_tool_arguments(raw_args):
        if not raw_args:
            return {}
        if isinstance(raw_args, dict):
            return raw_args
        try:
            return json.loads(raw_args)
        except Exception:
            return {}

    @staticmethod
    def _extract_openai_text(response):
        chunks = []
        for item in response.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    chunks.append(content["text"])
        return "\n".join(chunks)
