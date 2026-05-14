import os
import runpy
import socket
import sys
import urllib.request
import builtins
from pathlib import Path


NATIVE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = NATIVE_ROOT.parent
if (REPO_ROOT / "bridge" / "3dsmax_bridge.py").exists():
    BRIDGE_SCRIPT = REPO_ROOT / "bridge" / "3dsmax_bridge.py"
else:
    BRIDGE_SCRIPT = REPO_ROOT / "3dsmax-bridge" / "3dsmax_bridge.py"
DEFAULT_BRIDGE_PORT = 7171
DEFAULT_MCP_PORT = 3001
PORT_STATE_NAME = "_threedsmax_mcp_native_ports"


def _ensure_import_path():
    native_path = str(NATIVE_ROOT)
    if native_path not in sys.path:
        sys.path.insert(0, native_path)


def _find_free_port(start_port):
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.settimeout(0.2)
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                continue

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("Could not find a free localhost port starting at {0}".format(start_port))


def _configure_instance_ports():
    existing = getattr(builtins, PORT_STATE_NAME, None)
    if existing:
        bridge_port = existing["bridge_port"]
        mcp_port = existing["mcp_port"]
    else:
        bridge_port = _find_free_port(DEFAULT_BRIDGE_PORT)
        mcp_port = _find_free_port(DEFAULT_MCP_PORT)
        setattr(builtins, PORT_STATE_NAME, {
            "bridge_port": bridge_port,
            "mcp_port": mcp_port,
        })

    os.environ["MAX_BRIDGE_URL"] = "http://127.0.0.1:{0}/execute".format(bridge_port)
    os.environ["MAX_BRIDGE_PORT"] = str(bridge_port)
    os.environ["THREEDSMAX_MCP_PORT"] = str(mcp_port)
    os.environ["THREEDSMAX_MCP_URL"] = "http://127.0.0.1:{0}".format(mcp_port)
    return bridge_port, mcp_port


def _bridge_health_url():
    return "http://127.0.0.1:{0}/health".format(os.environ["MAX_BRIDGE_PORT"])


def _bridge_is_running():
    try:
        with urllib.request.urlopen(_bridge_health_url(), timeout=1.5) as response:
            return response.status == 200
    except Exception:
        return False


def _ensure_bridge():
    if _bridge_is_running():
        return
    runpy.run_path(str(BRIDGE_SCRIPT), run_name="__mcp_bridge__")


def launch():
    _configure_instance_ports()
    _ensure_import_path()
    _ensure_bridge()

    from app.ui import show

    return show()


launch()
