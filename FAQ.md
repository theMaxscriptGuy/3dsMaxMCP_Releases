# 3ds Max AI Assistant FAQ

## What is 3ds Max AI Assistant?

3ds Max AI Assistant is a native AI workflow companion for Autodesk 3ds Max. It
lets users control scene operations through natural language from inside 3ds Max.

## Who is it for?

It is for 3D artists, designers, visualization teams, technical artists,
automation engineers, and studios using Autodesk 3ds Max.

## What problem does it solve?

It reduces repetitive manual work in 3ds Max by allowing users to create, edit,
inspect, and automate scene tasks using conversational commands.

## How does the user install it?

Open 3ds Max and run:

```text
install_3dsmax_ai.ms
```

The script installs a 3ds Max action under:

```text
Category: 3ds Max AI Assistant
Action: Open 3ds Max AI Assistant
```

## Does the user need Node.js or npm?

No. The packaged release includes a local server executable:

```text
bin\3dsmax-mcp-server.exe
```

## How does the tool work technically?

The product has three main parts:

```text
Native 3ds Max UI -> Local MCP Server -> 3ds Max Python Bridge
```

The UI collects user commands, the MCP server coordinates LLM/tool calls, and
the Python bridge executes approved commands inside 3ds Max.

## Which AI providers are supported?

Current supported providers are:

- OpenAI
- OpenRouter
- Anthropic

## Can users choose models?

Yes. Users can enter model names manually. For OpenRouter, they can also load
available tool-capable models into a dropdown.

## Does it support AI-generated 3D models?

Yes, optionally through Meshy integration. Users can create 3D assets from text
or image references, then import generated FBX models into 3ds Max.

## Does Meshy cost credits?

Yes. Meshy credit-spending operations require explicit user confirmation in the
prompt, such as:

```text
I confirm spending credits.
```

## Can users attach images?

Yes. The native UI supports attaching `.png`, `.jpg`, and `.jpeg` files for
Meshy image-to-3D workflows.

## Can multiple 3ds Max instances run at once?

Yes. The native UI supports configurable MCP and bridge ports so different
3ds Max instances can run separate local connections.

## Does it work without the web UI?

Yes. The native 3ds Max UI is a complete frontend. The web UI can still exist as
an alternate frontend, but users do not need it for the packaged release.

## Where are API keys stored?

Currently, API keys are entered by the user in the UI and are not bundled in the
package. Long-term secure local settings storage can be added later.

## What is included in the packaged release?

```text
bin\3dsmax-mcp-server.exe
bridge\3dsmax_bridge.py
max\launch_native_ui.py
max\app\
install_3dsmax_ai.ms
README.md
```

## What is not included?

The package does not include:

- User API keys
- Meshy credits
- Autodesk 3ds Max
- A cloud backend
- A public hosted service

## What is the primary MVP success metric?

A user can install the package, open the assistant inside 3ds Max, start the
local server, connect, and create or modify a scene object using natural
language.

## What is an example command?

```text
Create a cityscape using boxes only. Make sure to use max 50 boxes. 
```

## What are the main risks?

- Some LLM models may not support tool calling reliably.
- Antivirus may block the packaged server executable.
- 3ds Max Python/Qt behavior can vary by version.
- Meshy API behavior and pricing can change over time.
- Local desktop packaging needs careful install/uninstall handling.

## What are future improvements?

- Windows installer
- Auto-update support
- Secure local API key storage
- Better model recommendations
- More 3ds Max tools
- Asset library workflows
- Render setup automation
- Studio/team configuration presets
