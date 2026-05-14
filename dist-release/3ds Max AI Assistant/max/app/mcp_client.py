import json
import queue
import threading
import urllib.error
import urllib.request

from .settings import MCP_SERVER_URL


class MCPClient:
    def __init__(self, server_url=MCP_SERVER_URL):
        self.server_url = server_url.rstrip("/")
        self.session_id = None
        self.tools = []
        self._next_id = 1
        self._pending = {}
        self._pending_lock = threading.Lock()
        self._session_queue = queue.Queue()
        self._reader_thread = None
        self._closed = False

    def connect(self):
        self._closed = False
        self._reader_thread = threading.Thread(target=self._read_sse, daemon=True)
        self._reader_thread.start()
        session_result = self._session_queue.get(timeout=10)
        if isinstance(session_result, Exception):
            raise RuntimeError("Could not connect to MCP SSE: {0}".format(session_result))
        self.session_id = session_result

        self._send_rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "3dsmax-native-ui", "version": "1.0.0"},
            "capabilities": {},
        })
        result = self._send_rpc("tools/list", {})
        self.tools = result.get("tools", [])
        return self.tools

    def disconnect(self):
        self._closed = True
        self.session_id = None

    def call_tool(self, name, arguments=None):
        return self._send_rpc("tools/call", {
            "name": name,
            "arguments": arguments or {},
        })

    def anthropic_tools(self):
        return [
            {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool.get("inputSchema", {"type": "object"}),
            }
            for tool in self.tools
        ]

    def openai_tools(self):
        return [
            {
                "type": "function",
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("inputSchema", {"type": "object"}),
            }
            for tool in self.tools
        ]

    def openai_chat_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {"type": "object"}),
                },
            }
            for tool in self.tools
        ]

    def _read_sse(self):
        try:
            request = urllib.request.Request(f"{self.server_url}/sse")
            with urllib.request.urlopen(request, timeout=30) as response:
                event_name = "message"
                data_lines = []

                for raw_line in response:
                    if self._closed:
                        break

                    line = raw_line.decode("utf-8").rstrip("\n")
                    if line.startswith("event:"):
                        event_name = line.split(":", 1)[1].strip()
                    elif line.startswith("data:"):
                        data_lines.append(line.split(":", 1)[1].strip())
                    elif line == "":
                        if data_lines:
                            self._handle_sse_event(event_name, "\n".join(data_lines))
                        event_name = "message"
                        data_lines = []
        except Exception as exc:
            if self.session_id is None:
                self._session_queue.put(exc)

    def _handle_sse_event(self, event_name, data):
        payload = json.loads(data)

        if event_name == "session":
            self._session_queue.put(payload["sessionId"])
            return

        if event_name != "message":
            return

        message_id = payload.get("id")
        if message_id is None:
            return

        with self._pending_lock:
            pending = self._pending.pop(message_id, None)

        if not pending:
            return

        event, holder = pending
        holder["payload"] = payload
        event.set()

    def _send_rpc(self, method, params):
        if not self.session_id:
            raise RuntimeError("Not connected to MCP server.")

        message_id = self._next_id
        self._next_id += 1

        event = threading.Event()
        holder = {}
        with self._pending_lock:
            self._pending[message_id] = (event, holder)

        body = json.dumps({
            "jsonrpc": "2.0",
            "id": message_id,
            "method": method,
            "params": params,
        }).encode("utf-8")

        request = urllib.request.Request(
            f"{self.server_url}/message/{self.session_id}",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(request, timeout=10).read()

        if not event.wait(60):
            with self._pending_lock:
                self._pending.pop(message_id, None)
            raise TimeoutError(f"RPC timeout for {method}")

        payload = holder["payload"]
        if payload.get("error"):
            raise RuntimeError(payload["error"].get("message", "MCP error"))
        return payload.get("result", {})
