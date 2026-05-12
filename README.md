# 3ds Max MCP Releases

Release repository for the 3ds Max MCP tool.

This repository is intended to hold the files needed to install and run the 3ds Max MCP integration, including:

- 3ds Max plugin Python scripts
- MCP server executable builds
- Release notes and setup instructions

## Repository Layout

The release package should be organized so users can quickly identify what needs to be copied into 3ds Max and what needs to be run as the MCP server.

```text
.
+-- plugins/
|   +-- 3ds Max Python plugin scripts
+-- server/
|   +-- MCP server executable and supporting files
+-- docs/
|   +-- Additional setup or troubleshooting notes
+-- README.md
```

If a release uses a different layout, document the exact file locations in the release notes.

## Requirements

- Autodesk 3ds Max
- Python support enabled in 3ds Max
- A compatible MCP client
- Windows environment capable of running the included MCP server executable

Version-specific requirements will be added once the supported 3ds Max versions, Python version, and server runtime details are finalized.

## Installation

### 1. Install the 3ds Max Plugin Scripts

Copy the provided plugin Python script files into the appropriate 3ds Max scripts or startup scripts location.

The exact install path depends on the final plugin packaging and target 3ds Max version. Add the confirmed destination path here before release.

### 2. Install the MCP Server

Place the MCP server executable and any supporting files in a stable local directory.

Recommended example:

```text
C:\mcp\3dsmax-mcp\
```

Keep the server executable, configuration files, and required runtime files together unless the release notes say otherwise.

### 3. Configure Your MCP Client

Add the 3ds Max MCP server to your MCP client configuration.

The final configuration block will be added once the executable name, command arguments, and environment variables are confirmed.

## Usage

1. Start 3ds Max.
2. Make sure the plugin scripts are loaded.
3. Start or connect through the MCP server using your MCP client.
4. Use the MCP client to send supported commands to 3ds Max.

Detailed command examples will be added after the tool interface and supported operations are finalized.

## Release Notes

Each release should include:

- Release version
- Supported 3ds Max versions
- Included plugin script files
- Included MCP server executable version
- New features
- Fixes
- Known issues
- Upgrade notes, if applicable

## Troubleshooting

Common areas to check:

- Confirm 3ds Max has loaded the plugin Python scripts.
- Confirm the MCP server executable starts without errors.
- Confirm the MCP client configuration points to the correct executable path.
- Confirm any required ports, permissions, or local security prompts are allowed.

More specific troubleshooting steps will be added as packaging and runtime details are finalized.

## Development Notes

This repository is for release-ready files, not necessarily the full development source tree. Keep committed files focused on installable plugin scripts, server binaries, documentation, and release metadata.

## License

This project is licensed under the terms in [LICENSE.md](LICENSE.md).

Any use, redistribution, modification, or public reference to this project must include clear credit to the creator:

```text
Created by Videep Mishraa
```

## Details To Add

The following details are still pending and can be filled in as they become available:

- Official tool name
- Supported 3ds Max versions
- Plugin script filenames
- Final install paths
- MCP server executable name
- MCP client configuration example
- Startup workflow
- Supported commands or features
- Known limitations
