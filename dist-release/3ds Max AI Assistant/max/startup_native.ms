-- Optional helper for launching the native Python UI from 3ds Max.
-- Edit nativeUiPath if this repository lives somewhere else.

macroScript ThreeDsMaxMcpNativeUI
category:"3ds Max MCP"
tooltip:"Open 3ds Max MCP Native UI"
buttonText:"MCP AI"
(
    on execute do
    (
        nativeUiPath = @"C:\mcp\3dsmax-mcp\3dsmax-native\launch_native_ui.py"
        python.ExecuteFile nativeUiPath
    )
)
