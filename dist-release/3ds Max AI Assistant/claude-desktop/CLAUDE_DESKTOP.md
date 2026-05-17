# Claude Desktop

This package includes a dedicated local MCP executable for Claude Desktop:

```text
bin\3dsmax-claude-mcp.exe
```

## Setup

1. Start 3ds Max and open the assistant once so the bridge is running.
2. In Claude Desktop, open `Settings > Developer > Edit Config`.
3. Add an `mcpServers` entry like this, changing the path if you installed the
   package somewhere else:

```json
{
  "mcpServers": {
    "3dsmax": {
      "command": "C:\\Path\\To\\3ds Max AI Assistant\\bin\\3dsmax-claude-mcp.exe",
      "env": {
        "MAX_BRIDGE_URL": "http://127.0.0.1:7171/execute"
      }
    }
  }
}
```

4. Fully quit and reopen Claude Desktop.
5. Try:

```text
List the objects in the current 3ds Max scene.
```

If you changed the 3ds Max bridge port from the default `7171`, update
`MAX_BRIDGE_URL` in the Claude Desktop config to match it.
