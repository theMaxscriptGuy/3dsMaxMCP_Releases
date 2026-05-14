# 3ds Max MCP Releases

Release repository for the 3ds Max MCP / 3ds Max AI Assistant package.

## Current Release Package

The installable package is in:

```text
dist-release\3ds Max AI Assistant\
```

Package contents:

```text
dist-release\
+-- 3ds Max AI Assistant\
|   +-- install_3dsmax_ai.ms
|   +-- README.md
|   +-- bin\
|   |   +-- 3dsmax-mcp-server.exe
|   +-- bridge\
|   |   +-- 3dsmax_bridge.py
|   +-- max\
|       +-- launch_native_ui.py
|       +-- startup_native.ms
|       +-- app\
|           +-- Native 3ds Max UI Python package
+-- server\
    +-- 3dsmax-mcp-server.exe
USER_INSTALL_AND_USE.html
```

Use `dist-release\3ds Max AI Assistant` as the user-facing package. The
`server` folder keeps a standalone copy of the packaged MCP server executable.

For a browser-friendly install guide, open:

```text
USER_INSTALL_AND_USE.html
```

## Requirements

- Autodesk 3ds Max with Python support enabled
- Windows environment capable of running `3dsmax-mcp-server.exe`
- Provider API key for OpenAI, OpenRouter, or Anthropic when using the native UI
- Optional: Meshy API key for Meshy-backed workflows
- Optional: `qt-material` installed in the 3ds Max Python environment for the enhanced theme

The native UI falls back to a built-in Qt stylesheet if `qt-material` is not
installed.

## Installation

For end users, the simplest instructions are in `USER_INSTALL_AND_USE.html`.

1. Copy `dist-release\3ds Max AI Assistant` to a stable local folder.
2. In 3ds Max, run:

```text
dist-release\3ds Max AI Assistant\install_3dsmax_ai.ms
```

The installer creates a user macro:

```text
Category: 3ds Max AI Assistant
Action: Open 3ds Max AI Assistant
```

Add that action to a toolbar, menu, quad menu, or hotkey from 3ds Max's
customize UI tools.

## Manual Launch

If you do not want to install the macro, open 3ds Max and run:

```text
dist-release\3ds Max AI Assistant\max\launch_native_ui.py
```

The launcher starts the local bridge in 3ds Max if needed, then opens the native
assistant UI.

## Usage

1. Start 3ds Max.
2. Open the `3ds Max AI Assistant` action, or run `max\launch_native_ui.py`.
3. Click `Start Server` if the MCP server is not already running.
4. Choose OpenAI, OpenRouter, or Anthropic.
5. Enter the provider API key and confirm the model.
6. Click `Connect`.
7. Send natural-language commands to control the 3ds Max scene.

The native UI starts the packaged server from:

```text
dist-release\3ds Max AI Assistant\bin\3dsmax-mcp-server.exe
```

## Ports

The native launcher assigns each 3ds Max instance a local bridge/MCP port pair.
Defaults begin at:

```text
Bridge: 7171
MCP:    3001
```

Additional 3ds Max instances use the next available local ports.

## Troubleshooting

- Confirm the package folder was not moved after running the installer. If it
  was moved, run `install_3dsmax_ai.ms` again from the new location.
- Confirm `bin\3dsmax-mcp-server.exe` is present and allowed by Windows security.
- Confirm 3ds Max can run Python scripts.
- Confirm no other process is blocking the selected bridge or MCP ports.
- If the enhanced theme is missing, install `qt-material` into the 3ds Max
  Python environment, or use the built-in fallback theme.

## License

This project is licensed under the terms in [LICENSE.md](LICENSE.md).

Any use, redistribution, modification, or public reference to this project must
include clear credit to the creator:

```text
Created by Videep Mishraa
```
