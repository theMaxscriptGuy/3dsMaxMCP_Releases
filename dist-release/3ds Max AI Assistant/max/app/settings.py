import os
import builtins
from pathlib import Path


NATIVE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = NATIVE_ROOT.parent
MCP_SERVER_DIR = REPO_ROOT / "mcp-server"
MCP_SERVER_EXE = Path(os.environ.get("THREEDSMAX_MCP_SERVER_EXE", REPO_ROOT / "bin" / "3dsmax-mcp-server.exe"))

if (REPO_ROOT / "bridge" / "3dsmax_bridge.py").exists():
    BRIDGE_SCRIPT = REPO_ROOT / "bridge" / "3dsmax_bridge.py"
else:
    BRIDGE_SCRIPT = REPO_ROOT / "3dsmax-bridge" / "3dsmax_bridge.py"

MCP_SERVER_PORT = int(os.environ.get("THREEDSMAX_MCP_PORT", "3001"))
BRIDGE_PORT = int(os.environ.get("MAX_BRIDGE_PORT", "7171"))

MCP_SERVER_URL = os.environ.get("THREEDSMAX_MCP_URL", "http://127.0.0.1:{0}".format(MCP_SERVER_PORT))
MAX_BRIDGE_URL = os.environ.get("MAX_BRIDGE_URL", "http://127.0.0.1:{0}/execute".format(BRIDGE_PORT))
BRIDGE_HEALTH_URL = "http://127.0.0.1:{0}/health".format(BRIDGE_PORT)
PORT_STATE_NAME = "_threedsmax_mcp_native_ports"
MESHY_TEST_API_KEY = "msy_dummy_api_key_for_test_mode_12345678"
MESHY_ENABLED = os.environ.get("MESHY_ENABLED", "").lower() in ("1", "true", "yes", "on")
MESHY_API_KEY = os.environ.get("MESHY_API_KEY", "")


def apply_runtime_ports(mcp_port, bridge_port):
    global MCP_SERVER_PORT, BRIDGE_PORT, MCP_SERVER_URL, MAX_BRIDGE_URL, BRIDGE_HEALTH_URL

    MCP_SERVER_PORT = int(mcp_port)
    BRIDGE_PORT = int(bridge_port)
    MCP_SERVER_URL = "http://127.0.0.1:{0}".format(MCP_SERVER_PORT)
    MAX_BRIDGE_URL = "http://127.0.0.1:{0}/execute".format(BRIDGE_PORT)
    BRIDGE_HEALTH_URL = "http://127.0.0.1:{0}/health".format(BRIDGE_PORT)

    os.environ["THREEDSMAX_MCP_PORT"] = str(MCP_SERVER_PORT)
    os.environ["MAX_BRIDGE_PORT"] = str(BRIDGE_PORT)
    os.environ["THREEDSMAX_MCP_URL"] = MCP_SERVER_URL
    os.environ["MAX_BRIDGE_URL"] = MAX_BRIDGE_URL

    setattr(builtins, PORT_STATE_NAME, {
        "bridge_port": BRIDGE_PORT,
        "mcp_port": MCP_SERVER_PORT,
    })


def apply_meshy_settings(enabled, api_key):
    global MESHY_ENABLED, MESHY_API_KEY

    MESHY_ENABLED = bool(enabled)
    MESHY_API_KEY = str(api_key or "").strip()

    if MESHY_ENABLED:
        os.environ["MESHY_ENABLED"] = "true"
        os.environ["MESHY_API_KEY"] = MESHY_API_KEY
    else:
        os.environ.pop("MESHY_ENABLED", None)
        os.environ.pop("MESHY_API_KEY", None)

MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-5.4-mini",
    "openrouter": "openai/gpt-4o-mini",
}

MAX_RESPONSE_TOKENS = 8192

SYSTEM_PROMPT = """
You are an AI assistant that controls Autodesk 3ds Max through a set of tools.
When the user asks you to create, modify, or delete objects in the 3D scene,
use the available tools to do so. Be concise in your responses - briefly confirm
what you did, and ask for clarification only if the request is genuinely ambiguous.

Examples:
- "create a pink sphere" -> use create_sphere, then set_wirecolor or apply_standard_material
- "make a box and a cylinder next to each other" -> call create_box and create_cylinder with appropriate positions
- "delete all red spheres" -> use list_objects first, then delete_object for each matching name
- "move the sphere to 0,0,50" -> use move_object

Always give objects sensible names like "Sphere01", "Box_Floor", etc.
""".strip()
