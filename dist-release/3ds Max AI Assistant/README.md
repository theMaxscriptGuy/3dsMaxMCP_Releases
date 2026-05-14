# 3ds Max AI Assistant

Native 3ds Max Python UI for the packaged MCP server and 3ds Max bridge.

The release package is self-contained:

```text
max\launch_native_ui.py -> bin\3dsmax-mcp-server.exe -> bridge\3dsmax_bridge.py -> 3ds Max
```

## Install

1. Copy this `3ds Max AI Assistant` folder to a stable local location.
2. In 3ds Max, run `install_3dsmax_ai.ms`.
3. Add the installed action to a toolbar/menu/hotkey from:

```text
Category: 3ds Max AI Assistant
Action: Open 3ds Max AI Assistant
```

## Run from 3ds Max

1. Open 3ds Max.
2. Launch the installed `Open 3ds Max AI Assistant` action, or run `max\launch_native_ui.py` from the Python interpreter.
3. Click **Start Server** if the MCP server is not already running.
4. Choose OpenAI, OpenRouter, or Anthropic.
5. Confirm or edit the model name. For OpenRouter, click **Load Models** to
   populate the dropdown with tool-capable OpenRouter models.
6. Enter your provider API key.
7. Click **Connect**.
8. Send natural-language commands.

The launcher also checks whether the bridge is alive. If not, it loads
`bridge\3dsmax_bridge.py`, which starts the local bridge inside Max.

## Theme

The native UI uses `qt-material` when it is available:

```cmd
<3ds Max Python>\python.exe -m pip install qt-material
```

If `qt-material` is not installed, the UI falls back to a built-in dark/cyan
Qt stylesheet, so the app still runs without extra packages.

## Meshy

On branches that include Meshy integration, the native UI can enable Meshy when
it starts the MCP server:

1. Check **Enable Meshy**.
2. Paste your Meshy API key, or click **Use Test Key** for Meshy's documented
   development key.
3. Click **Start Server**.
4. Click **Connect** after the server starts.

This passes `MESHY_ENABLED=true` and `MESHY_API_KEY=<key>` to the Node MCP
server process. If Meshy is unchecked, no Meshy tools are exposed.

Use **Attach Images** to select local `.jpg`, `.jpeg`, or `.png` reference
images for Meshy image-to-3D. Then ask for something like:

```text
Use the attached image to create a Meshy image-to-3D FBX model. I confirm spending credits.
```

## Multiple 3ds Max Instances

The native launcher assigns each Max instance its own local port pair:

```text
Max A: bridge 7171, MCP 3001
Max B: bridge 7172, MCP 3002
Max C: bridge 7173, MCP 3003
```

The web UI defaults are unchanged. When you run the native UI, it sets:

```text
MAX_BRIDGE_PORT=<assigned bridge port>
MAX_BRIDGE_URL=http://127.0.0.1:<assigned bridge port>/execute
THREEDSMAX_MCP_PORT=<assigned MCP port>
THREEDSMAX_MCP_URL=http://127.0.0.1:<assigned MCP port>
```

Then it starts `bin\3dsmax-mcp-server.exe` with that MCP port and bridge URL. This keeps
commands from one Max instance routed to that same Max instance.

## Notes

- This UI intentionally duplicates the web UI chat loop in Python.
- Only one frontend is expected to be used at a time.
- Scene edits are still executed by the existing bridge queue on the 3ds Max main thread.
