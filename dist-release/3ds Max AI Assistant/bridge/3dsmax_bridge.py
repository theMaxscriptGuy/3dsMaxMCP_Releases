"""
3dsmax_bridge.py
================
Run this script from within 3ds Max (Scripting > Run Script, or drag-drop into
the MAXScript listener and call start_bridge()).

It starts a tiny HTTP server on localhost:7171 that accepts POST requests
with a JSON body:  { "code": "import MaxPlus; ..." }

The code is executed inside 3ds Max's Python interpreter (MaxPlus / pymxs).
The response is:  { "result": "...", "error": null }
                or { "result": null,  "error": "..." }

Usage inside 3ds Max:
    python.ExecuteFile @"C:\\path\\to\\3dsmax_bridge.py"
Or paste the whole file into the MAXScript Listener Python tab and run it.
"""

import threading
import json
import sys
import traceback
import queue
import builtins
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Try pymxs (3ds Max 2020+), fall back to MaxPlus
try:
    import pymxs
    RT = pymxs.runtime          # MAXScript runtime — use as RT.Sphere(), etc.
    BACKEND = "pymxs"
except ImportError:
    import MaxPlus
    RT = None
    BACKEND = "MaxPlus"

PORT = int(os.environ.get("MAX_BRIDGE_PORT", "7171"))
_server_instance = None
_server_thread   = None
_request_queue   = queue.Queue()
_active_requests = 0
_active_lock     = threading.Lock()


class ExecutionRequest:
    def __init__(self, code: str):
        self.code = code
        self.result = None
        self.error = None
        self.done = threading.Event()


# ─── Execution helpers ────────────────────────────────────────────────────────

def _exec_code(code: str):
    """
    Execute Python code in the 3ds Max context.
    Returns (result_str, error_str).
    """
    local_ns = {
        "RT": RT,
        "pymxs": sys.modules.get("pymxs"),
        "MaxPlus": sys.modules.get("MaxPlus"),
    }
    # Capture stdout
    import io
    stdout_capture = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout_capture
    error = None
    try:
        exec(compile(code, "<mcp>", "exec"), local_ns)   # noqa: S102
    except Exception:
        error = traceback.format_exc()
    finally:
        sys.stdout = old_stdout

    output = stdout_capture.getvalue().strip()
    return output, error


def _process_pending_requests():
    """
    Called by a MaxScript timer on 3ds Max's main thread.
    This keeps scene edits out of the HTTP server thread.
    """
    while True:
        try:
            request = _request_queue.get_nowait()
        except queue.Empty:
            break

        global _active_requests

        with _active_lock:
            _active_requests += 1

        try:
            request.result, request.error = _exec_code(request.code)
        finally:
            with _active_lock:
                _active_requests -= 1
            request.done.set()


def _bridge_status():
    with _active_lock:
        active_requests = _active_requests

    return {
        "status": "ok",
        "backend": BACKEND,
        "port": PORT,
        "busy": active_requests > 0,
        "active_requests": active_requests,
        "queue_size": _request_queue.qsize(),
    }


def _execute_on_main_thread(code: str, timeout: float = 30.0):
    if BACKEND != "pymxs":
        return _exec_code(code)

    request = ExecutionRequest(code)
    _request_queue.put(request)

    if not request.done.wait(timeout):
        return None, "Timed out waiting for 3ds Max main thread to execute the command."

    return request.result, request.error


def _install_main_thread_pump():
    if BACKEND != "pymxs":
        return

    builtins._mcp_bridge_process_pending = _process_pending_requests
    RT.execute(r'''
global mcpBridgePumpRollout
try (destroyDialog mcpBridgePumpRollout) catch()
rollout mcpBridgePumpRollout "MCP Bridge Pump" width:1 height:1
(
    timer bridgeTimer interval:50 active:true
    on bridgeTimer tick do
    (
        python.Execute "import builtins; builtins._mcp_bridge_process_pending()"
    )
)
createDialog mcpBridgePumpRollout 1 1 pos:[-32000,-32000] style:#(#style_toolwindow)
''')


def _uninstall_main_thread_pump():
    if BACKEND != "pymxs":
        return

    try:
        RT.execute("try (destroyDialog mcpBridgePumpRollout) catch()")
    except Exception:
        pass

    if hasattr(builtins, "_mcp_bridge_process_pending"):
        delattr(builtins, "_mcp_bridge_process_pending")


# ─── HTTP Request Handler ─────────────────────────────────────────────────────

class BridgeHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):  # silence default access log
        pass

    def _send_json(self, status: int, body: dict):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "http://localhost:3001")  # MCP server
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "http://localhost:3001")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, _bridge_status())
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/execute":
            self._send_json(404, {"error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            raw    = self.rfile.read(length)
            body   = json.loads(raw)
            code   = body.get("code", "")
        except Exception as e:
            self._send_json(400, {"result": None, "error": f"Bad request: {e}"})
            return

        print(f"[3dsmax-bridge] Executing:\n{code[:200]}")
        result, error = _execute_on_main_thread(code)

        if error:
            print(f"[3dsmax-bridge] Error: {error}")
            self._send_json(200, {"result": None, "error": error})
        else:
            self._send_json(200, {"result": result or "OK", "error": None})


# ─── Server lifecycle ─────────────────────────────────────────────────────────

def start_bridge(port: int = PORT):
    global _server_instance, _server_thread

    if _server_instance is not None:
        print(f"[3dsmax-bridge] Already running on port {port}")
        return

    _install_main_thread_pump()

    _server_instance = ThreadingHTTPServer(("127.0.0.1", port), BridgeHandler)
    _server_thread   = threading.Thread(
        target=_server_instance.serve_forever,
        daemon=True,
        name="3dsmax-mcp-bridge"
    )
    _server_thread.start()
    print(f"[3dsmax-bridge] ✅ Listening on http://127.0.0.1:{port}/execute  (backend: {BACKEND})")


def stop_bridge():
    global _server_instance, _server_thread
    if _server_instance:
        _server_instance.shutdown()
        _server_instance = None
        _server_thread   = None
        _uninstall_main_thread_pump()
        print("[3dsmax-bridge] Stopped.")
    else:
        print("[3dsmax-bridge] Not running.")


# Auto-start when the file is run/executed
start_bridge()
