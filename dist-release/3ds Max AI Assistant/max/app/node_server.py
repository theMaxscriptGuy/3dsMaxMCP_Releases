import subprocess
import time
import os
import urllib.error
import urllib.request

from . import settings


class NodeServerManager:
    def __init__(self):
        self.process = None

    def is_running(self):
        try:
            with urllib.request.urlopen(f"{settings.MCP_SERVER_URL}/health", timeout=1.5) as response:
                return response.status == 200
        except Exception:
            return False

    @property
    def server_url(self):
        return settings.MCP_SERVER_URL

    def start(self):
        if self.is_running():
            return "MCP server is already running on {0}.".format(settings.MCP_SERVER_URL)

        using_packaged_server = settings.MCP_SERVER_EXE.exists()
        command = [str(settings.MCP_SERVER_EXE)] if using_packaged_server else ["cmd", "/c", "npm", "start"]
        cwd = settings.MCP_SERVER_EXE.parent if using_packaged_server else settings.MCP_SERVER_DIR
        env = os.environ.copy()
        env["PORT"] = str(settings.MCP_SERVER_PORT)
        env["MAX_BRIDGE_URL"] = settings.MAX_BRIDGE_URL
        if settings.MESHY_ENABLED:
            env["MESHY_ENABLED"] = "true"
            env["MESHY_API_KEY"] = settings.MESHY_API_KEY
        else:
            env.pop("MESHY_ENABLED", None)
            env.pop("MESHY_API_KEY", None)

        self.process = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        for _ in range(30):
            if self.is_running():
                return "MCP server started on {0}.".format(settings.MCP_SERVER_URL)
            time.sleep(0.25)

        process_name = "packaged server" if using_packaged_server else "npm process"
        return "Started {0}, but MCP server did not answer /health yet.".format(process_name)

    def stop_if_owned(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            return "Stopped MCP server started by native UI."
        return "No native-owned MCP server process to stop."
