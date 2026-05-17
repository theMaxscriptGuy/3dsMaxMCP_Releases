-- 3ds Max AI Assistant installer.
-- Resolve paths from the installer file itself so the release package remains
-- portable after it is copied to another machine or folder.

(
    local installerPath = getSourceFileName()
    local packageRoot = pathConfig.removePathLeaf installerPath
    local launcherPath = packageRoot + @"\max\launch_native_ui.py"
    local macrosDir = getDir #userMacros
    local macroPath = macrosDir + @"\ThreeDsMaxAIAssistant.mcr"

    if not doesFileExist launcherPath then
    (
        messageBox ("Could not find launcher:\n" + launcherPath) title:"3ds Max AI Assistant"
        return false
    )

    local macroText = ""
    macroText += "macroScript ThreeDsMaxAIAssistant_Open\n"
    macroText += "category:\"3ds Max AI Assistant\"\n"
    macroText += "tooltip:\"Open 3ds Max AI Assistant\"\n"
    macroText += "buttonText:\"AI Assistant\"\n"
    macroText += "(\n"
    macroText += "    on execute do\n"
    macroText += "    (\n"
    macroText += ("        python.ExecuteFile @\"" + launcherPath + "\"\n")
    macroText += "    )\n"
    macroText += ")\n"

    local stream = createFile macroPath
    format "%" macroText to:stream
    close stream

    fileIn macroPath

    messageBox (
        "Installed 3ds Max AI Assistant.\n\n" +
        "Add it to a toolbar/menu from:\n" +
        "Category: 3ds Max AI Assistant\n" +
        "Action: Open 3ds Max AI Assistant"
    ) title:"3ds Max AI Assistant"

    true
)
