# 3ds Max AI Assistant

Use AI inside Autodesk 3ds Max to create, edit, inspect, and manage scenes with
natural language.

## Install

1. Open 3ds Max.
2. Go to:

```text
Scripting > Run Script...
```

3. Select this file from this package folder:

```text
install_3dsmax_ai.ms
```

4. The installer adds a 3ds Max action.

5. Add or run the action from:

```text
Category: 3ds Max AI Assistant
Action: Open Assistant
```

If the action does not show immediately, restart 3ds Max and check the same
category again.

## Open The Tool

Run:

```text
3ds Max AI Assistant > Open Assistant
```

The assistant window opens inside 3ds Max.

## Basic Use

Use the top row in this order:

1. Click `Apply Ports`.
2. Click `Start Server`.
3. Choose `OpenAI`, `OpenRouter`, or `Anthropic`.
4. Enter your API key.
5. If using OpenRouter, click `Load Models` and choose a model.
6. Click `Connect`.
7. Type a command and click `Send`.

Example:

```text
Create a red sphere at 0,0,50
```

## Meshy

To use Meshy:

1. Check `Enable Meshy`.
2. Enter your Meshy API key.
3. Click `Start Server`.
4. Click `Connect`.

For image-to-3D:

1. Click `Attach Images`.
2. Select image files.
3. Ask the assistant to create a Meshy image-to-3D model.

Example:

```text
Use the attached image to create a Meshy image-to-3D FBX model. I confirm spending credits.
```

## Notes

- You do not need Node.js or npm.
- The local server starts from `bin\3dsmax-mcp-server.exe`.
- API keys are entered by you and are not included in this package.
- If the server does not start, check whether Windows security or antivirus is
  blocking `bin\3dsmax-mcp-server.exe`.
