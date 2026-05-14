# 3ds Max AI Assistant

Introducing 3ds Max AI Assistant, a native AI workflow companion for Autodesk
3ds Max. It lets artists, designers, and technical teams control 3ds Max with
natural language directly from inside the application.

Use it to create and edit scene objects, assign materials, modify transforms,
inspect scenes, run simple automation, and generate assets through your
preferred AI provider. The package includes a native 3ds Max Python UI, a local
MCP server, and a Python bridge that executes commands in the active 3ds Max
session.

Key capabilities:

- Natural-language control for 3ds Max scene operations
- Support for OpenAI, Anthropic, and OpenRouter
- Optional Meshy text-to-3D and image-to-3D workflows
- Multi-instance support with configurable local ports
- Bundled local server executable, so users do not need to run npm or Node
- Simple MaxScript install flow

## Install

1. Open Autodesk 3ds Max.
2. Go to `Scripting > Run Script...`.
3. Select and run:

```text
install_3dsmax_ai.ms
```

4. When the installer finishes, add the new action to a toolbar, menu, quad
   menu, or hotkey.

Look for this action in 3ds Max customization:

```text
Category: 3ds Max AI Assistant
Action: Open 3ds Max AI Assistant
```

If the action does not appear immediately, restart 3ds Max and check the same
category again.

## Open

Run `Open 3ds Max AI Assistant` from the toolbar, menu, quad menu, or hotkey
where you added it.

## Use

1. Click `Start Server`.
2. Choose `OpenAI`, `OpenRouter`, or `Anthropic`.
3. Enter your provider API key.
4. Click `Connect`.
5. Type a command and send it.

Example:

```text
Hey there! Can you tell me if there are any duplicate objects in the scene?
```

<img width="1918" height="779" alt="SimpleQC_1" src="https://github.com/user-attachments/assets/fcc51656-8815-4e3b-881c-9991925a0a93" />


```text
QC this file and save the output in JSON format.
```

## Meshy

Meshy is optional and requires your own Meshy API key.

1. Check `Enable Meshy`.
2. Enter your Meshy API key.
3. Click `Start Server`.
4. Click `Connect`.

For image-to-3D, click `Attach Images`, select `.png`, `.jpg`, or `.jpeg`
reference images, then send a prompt that confirms credit spending.

Example:

```text
Use the attached image to create a Meshy image-to-3D FBX model. I confirm spending credits.
```

## Troubleshooting

- If the action is missing, restart 3ds Max and check `Category: 3ds Max AI Assistant`.
- If the server does not start, allow `3dsmax-mcp-server.exe` through Windows
  security or antivirus prompts.
- If the package folder was moved after installation, run `install_3dsmax_ai.ms`
  again from the new location.
- API keys are entered by you and are not bundled with this package.

## License

This project is licensed under the terms in [LICENSE.md](LICENSE.md).

Created by Videep Mishraa.
