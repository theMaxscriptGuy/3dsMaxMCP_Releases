# 3ds Max AI Assistant - Install And Use

This guide describes the Phase 1 package install flow.

## Build The Package

Open PowerShell in the repo root:

```powershell
C:\mcp\3dsmax-mcp
```

Build the server exe:

```powershell
powershell -ExecutionPolicy Bypass -File .\release\build-server.ps1
```

Build the release package:

```powershell
powershell -ExecutionPolicy Bypass -File .\release\build-package.ps1
```

Confirm this file exists:

```text
C:\mcp\3dsmax-mcp\dist-release\3ds Max AI Assistant\bin\3dsmax-mcp-server.exe
```

## Install In 3ds Max

1. Open 3ds Max.
2. Go to `Scripting > Run Script...`.
3. Run:

```text
C:\mcp\3dsmax-mcp\dist-release\3ds Max AI Assistant\install_3dsmax_ai.ms
```

4. Add the installed action to a toolbar, menu, quad, or hotkey:

```text
Category: 3ds Max AI Assistant
Action: Open Assistant
```

## Use The Assistant

1. Run `Open Assistant` from 3ds Max.
2. Click `Apply Ports`.
3. Click `Start Server`.
4. Choose an LLM provider:
   - OpenAI
   - OpenRouter
   - Anthropic
5. Enter the provider API key.
6. For OpenRouter, optionally click `Load Models`.
7. Click `Connect`.
8. Send a command, for example:

```text
Create a red sphere at 0,0,50
```

## Meshy

To enable Meshy:

1. Check `Enable Meshy`.
2. Enter your Meshy API key.
3. Click `Start Server`.
4. Click `Connect`.

For image-to-3D:

1. Click `Attach Images`.
2. Select `.png`, `.jpg`, or `.jpeg` files.
3. Send a prompt like:

```text
Use the attached image to create a Meshy image-to-3D FBX model. I confirm spending credits.
```

## Notes

- The package uses `bin\3dsmax-mcp-server.exe`; users do not need to run `npm`.
- API keys are entered by the user and are not bundled with the package.
- If 3ds Max was already open during install, restart Max if the new macro action does not appear immediately.
