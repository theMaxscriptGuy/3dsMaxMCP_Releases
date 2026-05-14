-- Optional helper for launching the native Python UI from 3ds Max.

macroScript ThreeDsMaxMcpNativeUI
category:"3ds Max AI Assistant"
tooltip:"Open 3ds Max AI Assistant"
buttonText:"AI Assistant"
(
    on execute do
    (
        local scriptPath = getSourceFileName()
        local maxDir = getFilenamePath scriptPath
        nativeUiPath = maxDir + @"\launch_native_ui.py"
        python.ExecuteFile nativeUiPath
    )
)
