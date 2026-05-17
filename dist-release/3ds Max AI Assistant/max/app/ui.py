import json
import threading
import urllib.request

from .chat import ChatEngine
from .mcp_client import MCPClient
from .node_server import NodeServerManager
from . import settings
from .max_window import get_main_window
from .theme import apply_theme

try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets


class WorkerSignals(QtCore.QObject):
    message = QtCore.Signal(str, str)
    status = QtCore.Signal(str)
    tool_call = QtCore.Signal(str, str)
    usage = QtCore.Signal(object)
    models_loaded = QtCore.Signal(list)
    connected = QtCore.Signal(object, object, int)
    finished = QtCore.Signal()
    error = QtCore.Signal(str)


class ZoomablePlainTextEdit(QtWidgets.QPlainTextEdit):
    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn(1)
            elif delta < 0:
                self.zoomOut(1)
            event.accept()
            return

        super(ZoomablePlainTextEdit, self).wheelEvent(event)


class NativeAssistantWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(NativeAssistantWindow, self).__init__(parent)
        self.setWindowTitle("3ds Max AI Assistant")
        self.resize(760, 620)
        self.theme_name = ""

        self.server = NodeServerManager()
        self.mcp = None
        self.chat = None
        self.connected = False
        self.sending = False
        self.connecting = False
        self.starting_server = False
        self._server_signals = None
        self._connect_signals = None
        self._send_signals = None
        self._model_signals = None
        self.attached_image_paths = []

        self._build_ui()
        self._wire_events()
        self._refresh_status()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        top_row = QtWidgets.QHBoxLayout()
        self.server_status = QtWidgets.QLabel("MCP: Unknown")
        self.bridge_status = QtWidgets.QLabel("3ds Max: Unknown")
        self.port_status = QtWidgets.QLabel()
        self.port_status.setObjectName("portStatus")
        top_row.addWidget(self.server_status)
        top_row.addWidget(self.bridge_status)
        top_row.addWidget(self.port_status)
        top_row.addStretch(1)
        layout.addLayout(top_row)

        port_row = QtWidgets.QHBoxLayout()
        port_row.addWidget(QtWidgets.QLabel("MCP Port"))
        self.mcp_port_input = QtWidgets.QSpinBox()
        self.mcp_port_input.setRange(1024, 65535)
        self.mcp_port_input.setValue(settings.MCP_SERVER_PORT)
        port_row.addWidget(self.mcp_port_input)
        port_row.addWidget(QtWidgets.QLabel("Bridge Port"))
        self.bridge_port_input = QtWidgets.QSpinBox()
        self.bridge_port_input.setRange(1024, 65535)
        self.bridge_port_input.setValue(settings.BRIDGE_PORT)
        port_row.addWidget(self.bridge_port_input)
        self.apply_ports_button = QtWidgets.QPushButton("Apply Ports")
        self.start_server_button = QtWidgets.QPushButton("Start Server")
        self.stop_server_button = QtWidgets.QPushButton("Stop Server")
        self.connect_button = QtWidgets.QPushButton("Connect")
        port_row.addWidget(self.apply_ports_button)
        port_row.addWidget(self.start_server_button)
        port_row.addWidget(self.stop_server_button)
        port_row.addWidget(self.connect_button)
        port_row.addStretch(1)
        layout.addLayout(port_row)

        controls = QtWidgets.QHBoxLayout()
        self.provider_select = QtWidgets.QComboBox()
        self.provider_select.addItem("OpenAI", "openai")
        self.provider_select.addItem("OpenRouter", "openrouter")
        self.provider_select.addItem("Anthropic", "anthropic")
        self.model_input = QtWidgets.QComboBox()
        self.model_input.setEditable(True)
        self.model_input.setMinimumWidth(160)
        self.model_input.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.model_input.setMinimumContentsLength(27)
        self.model_input.addItem(settings.MODELS["openai"])
        self.model_input.setCurrentText(settings.MODELS["openai"])
        self.load_models_button = QtWidgets.QPushButton("Load Models")
        self.load_models_button.setEnabled(False)
        self.api_key_input = QtWidgets.QLineEdit()
        self.api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_key_input.setPlaceholderText("API key")
        self.clear_text_button = QtWidgets.QPushButton("Clear Text")
        controls.addWidget(self.provider_select)
        controls.addWidget(self.model_input)
        controls.addWidget(self.load_models_button)
        controls.addWidget(self.api_key_input, 1)
        controls.addWidget(self.clear_text_button)
        layout.addLayout(controls)

        meshy_row = QtWidgets.QHBoxLayout()
        self.meshy_enabled_input = QtWidgets.QCheckBox("Enable Meshy")
        self.meshy_enabled_input.setChecked(settings.MESHY_ENABLED)
        self.meshy_api_key_input = QtWidgets.QLineEdit()
        self.meshy_api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.meshy_api_key_input.setPlaceholderText("Meshy API key")
        self.meshy_api_key_input.setText(settings.MESHY_API_KEY)
        self.meshy_test_key_button = QtWidgets.QPushButton("Use Test Key")
        meshy_row.addWidget(self.meshy_enabled_input)
        meshy_row.addWidget(self.meshy_api_key_input, 1)
        meshy_row.addWidget(self.meshy_test_key_button)
        layout.addLayout(meshy_row)

        image_row = QtWidgets.QHBoxLayout()
        self.attach_images_button = QtWidgets.QPushButton("Attach Images")
        self.clear_images_button = QtWidgets.QPushButton("Clear Images")
        self.attached_images_label = QtWidgets.QLabel("No images attached")
        self.attached_images_label.setObjectName("portStatus")
        image_row.addWidget(self.attach_images_button)
        image_row.addWidget(self.clear_images_button)
        image_row.addWidget(self.attached_images_label, 1)
        layout.addLayout(image_row)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.messages = QtWidgets.QTextEdit()
        self.messages.setReadOnly(True)
        self.messages.setObjectName("messages")
        self.tool_log = QtWidgets.QTextEdit()
        self.tool_log.setReadOnly(True)
        self.tool_log.setObjectName("toolLog")
        self.tool_log.setMaximumWidth(260)
        splitter.addWidget(self.messages)
        splitter.addWidget(self.tool_log)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, 1)

        input_row = QtWidgets.QHBoxLayout()
        self.prompt_input = ZoomablePlainTextEdit()
        self.prompt_input.setPlaceholderText("e.g. Create a pink sphere called Orb01 at 0,0,30")
        self.prompt_input.setMaximumHeight(82)
        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.setEnabled(False)
        input_row.addWidget(self.prompt_input, 1)
        input_row.addWidget(self.send_button)
        layout.addLayout(input_row)

    def _wire_events(self):
        self.start_server_button.clicked.connect(self.start_server)
        self.stop_server_button.clicked.connect(self.stop_server)
        self.apply_ports_button.clicked.connect(self.apply_ports)
        self.meshy_test_key_button.clicked.connect(self.use_meshy_test_key)
        self.attach_images_button.clicked.connect(self.attach_images)
        self.clear_images_button.clicked.connect(self.clear_images)
        self.load_models_button.clicked.connect(self.load_openrouter_models)
        self.connect_button.clicked.connect(self.toggle_connection)
        self.clear_text_button.clicked.connect(self.clear_text_windows)
        self.send_button.clicked.connect(self.send_prompt)
        self.provider_select.currentIndexChanged.connect(self._provider_changed)

    def _refresh_status(self):
        self.server_status.setText("MCP: Connected" if self.server.is_running() else "MCP: Offline")
        if not self.connected and not self.connecting:
            self.connect_button.setEnabled(True)
        if not self.starting_server:
            self.start_server_button.setEnabled(True)
        self.port_status.setText("Ports: MCP {0}, Bridge {1}".format(
            settings.MCP_SERVER_PORT,
            settings.BRIDGE_PORT,
        ))
        if self.theme_name:
            self.port_status.setToolTip("Theme: {0}".format(self.theme_name))
        self._refresh_bridge_status()

    def _refresh_bridge_status(self):
        try:
            with urllib.request.urlopen(settings.BRIDGE_HEALTH_URL, timeout=1.5) as response:
                data = json.loads(response.read().decode("utf-8"))
            label = "3ds Max: Busy" if data.get("busy") or data.get("queue_size", 0) > 0 else "3ds Max: Ready"
            self.bridge_status.setText(label)
        except Exception:
            self.bridge_status.setText("3ds Max: Bridge Offline")

    def apply_ports(self):
        if self.connected:
            self._append("error", "Disconnect before changing ports.")
            return

        if self.server.is_running():
            self._append("error", "Stop the current MCP server or choose ports before starting it.")
            return

        old_bridge_port = settings.BRIDGE_PORT

        settings.apply_runtime_ports(
            self.mcp_port_input.value(),
            self.bridge_port_input.value(),
        )
        self._append("system", "Using MCP {0}, Bridge {1}.".format(
            settings.MCP_SERVER_PORT,
            settings.BRIDGE_PORT,
        ))
        if old_bridge_port != settings.BRIDGE_PORT and self._bridge_is_running(old_bridge_port):
            self._append("system", "Bridge {0} is already running. Restart this Max instance to move its bridge to {1}.".format(
                old_bridge_port,
                settings.BRIDGE_PORT,
            ))
        self._refresh_status()

    def _bridge_is_running(self, port):
        try:
            with urllib.request.urlopen("http://127.0.0.1:{0}/health".format(port), timeout=1.0) as response:
                return response.status == 200
        except Exception:
            return False

    def start_server(self):
        if not self.connected and not self.server.is_running():
            settings.apply_runtime_ports(
                self.mcp_port_input.value(),
                self.bridge_port_input.value(),
            )
        self.apply_meshy_settings()
        self._append("system", "Starting MCP server...")
        self._append("system", "Using MCP {0}, Bridge {1}.".format(
            settings.MCP_SERVER_PORT,
            settings.BRIDGE_PORT,
        ))
        if settings.MESHY_ENABLED:
            self._append("system", "Meshy enabled for this server start.")
        self.starting_server = True
        self.start_server_button.setEnabled(False)
        signals = WorkerSignals()
        self._server_signals = signals
        signals.status.connect(lambda message: self._append("system", message))
        signals.error.connect(lambda message: self._append("error", message))
        signals.finished.connect(self._after_server_start)

        def run():
            try:
                message = self.server.start()
                signals.status.emit(message)
            except Exception as exc:
                signals.error.emit(str(exc))
            finally:
                signals.finished.emit()

        threading.Thread(target=run, daemon=True).start()

    def _after_server_start(self):
        self.starting_server = False
        self.start_server_button.setEnabled(True)
        self._server_signals = None
        self._refresh_status()

    def stop_server(self):
        if self.connected:
            self.disconnect_mcp()
        message = self.server.stop_if_owned()
        self._append("system", message)
        self._refresh_status()

    def apply_meshy_settings(self):
        settings.apply_meshy_settings(
            self.meshy_enabled_input.isChecked(),
            self.meshy_api_key_input.text(),
        )

    def use_meshy_test_key(self):
        self.meshy_enabled_input.setChecked(True)
        self.meshy_api_key_input.setText(settings.MESHY_TEST_API_KEY)
        self._append("system", "Meshy test key selected. It is for development and should not consume credits.")

    def attach_images(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Attach reference images",
            "",
            "Images (*.png *.jpg *.jpeg)",
        )
        if not files:
            return

        for filepath in files:
            if filepath not in self.attached_image_paths:
                self.attached_image_paths.append(filepath)
        self._update_attached_images_label()

    def clear_images(self):
        self.attached_image_paths = []
        self._update_attached_images_label()

    def clear_text_windows(self):
        self.messages.clear()
        self.tool_log.clear()
        self.prompt_input.clear()

    def load_openrouter_models(self):
        if self.provider_select.currentData() != "openrouter":
            self._append("system", "Switch provider to OpenRouter before loading OpenRouter models.")
            return

        if not self._mcp_server_is_reachable():
            self._append(
                "error",
                "MCP server is not reachable at {0}. Start the server first, or apply the correct MCP port.".format(
                    settings.MCP_SERVER_URL,
                ),
            )
            return

        self.load_models_button.setEnabled(False)
        self._append("system", "Loading OpenRouter models...")
        signals = WorkerSignals()
        self._model_signals = signals
        signals.models_loaded.connect(self._finish_load_openrouter_models)
        signals.error.connect(lambda message: self._append("error", message))
        signals.finished.connect(self._finish_model_load_attempt)

        def run():
            try:
                request = urllib.request.Request(
                    "{0}/llm/openrouter/models".format(settings.MCP_SERVER_URL),
                    method="GET",
                    headers=self._openrouter_model_headers(),
                )
                with urllib.request.urlopen(request, timeout=30) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                models = sorted(
                    model.get("id")
                    for model in payload.get("data", [])
                    if model.get("id")
                )
                signals.models_loaded.emit(models)
            except Exception as exc:
                signals.error.emit("Could not load OpenRouter models: {0}".format(exc))
            finally:
                signals.finished.emit()

        threading.Thread(target=run, daemon=True).start()

    def _mcp_server_is_reachable(self):
        try:
            with urllib.request.urlopen("{0}/health".format(settings.MCP_SERVER_URL), timeout=1.5) as response:
                return response.status == 200
        except Exception:
            return False

    def _openrouter_model_headers(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            return {}
        return {"x-llm-api-key": api_key}

    def _finish_load_openrouter_models(self, models):
        current = self.model_input.currentText().strip()
        self.model_input.clear()
        self.model_input.addItems(models)
        if current:
            self.model_input.setCurrentText(current)
        elif models:
            self.model_input.setCurrentText(models[0])
        self._append("system", "Loaded {0} OpenRouter tool-capable models.".format(len(models)))

    def _finish_model_load_attempt(self):
        self.load_models_button.setEnabled(True)
        self._model_signals = None

    def _update_attached_images_label(self):
        if not self.attached_image_paths:
            self.attached_images_label.setText("No images attached")
            self.attached_images_label.setToolTip("")
            return

        names = [path.replace("\\", "/").split("/")[-1] for path in self.attached_image_paths]
        self.attached_images_label.setText("Attached: {0}".format(", ".join(names[:3])))
        self.attached_images_label.setToolTip("\n".join(self.attached_image_paths))

    def toggle_connection(self):
        if self.connected:
            self.disconnect_mcp()
        else:
            self.connect_mcp()

    def connect_mcp(self):
        self.connecting = True
        self.connect_button.setEnabled(False)
        self._append("system", "Connecting to MCP server...")
        signals = WorkerSignals()
        self._connect_signals = signals
        signals.connected.connect(self._finish_connect)
        signals.error.connect(lambda message: self._append("error", message))
        signals.finished.connect(self._finish_connect_attempt)

        def run():
            try:
                mcp = MCPClient()
                tools = mcp.connect()
                chat = ChatEngine(mcp)
                signals.connected.emit(mcp, chat, len(tools))
            except Exception as exc:
                signals.error.emit("Connection error: {0}".format(exc))
            finally:
                signals.finished.emit()

        threading.Thread(target=run, daemon=True).start()

    def _finish_connect(self, mcp, chat, tool_count):
        self.mcp = mcp
        self.chat = chat
        self.connected = True
        self.connecting = False
        self.connect_button.setText("Disconnect")
        self.connect_button.setEnabled(True)
        self.send_button.setEnabled(True)
        self._append("system", "Connected. {0} tools available.".format(tool_count))
        self._show_available_tools()
        self._refresh_status()

    def _finish_connect_attempt(self):
        self.connecting = False
        self.connect_button.setEnabled(True)
        self._connect_signals = None

    def disconnect_mcp(self):
        if self.mcp:
            self.mcp.disconnect()
        self.mcp = None
        self.chat = None
        self.connected = False
        self.connecting = False
        self.connect_button.setText("Connect")
        self.connect_button.setEnabled(True)
        self.send_button.setEnabled(False)
        self._append("system", "Disconnected from MCP server.")

    def send_prompt(self):
        text = self.prompt_input.toPlainText().strip()
        if not text or self.sending or not self.chat:
            return

        api_key = self.api_key_input.text().strip()
        if not api_key:
            self._append("error", "Enter your provider API key first.")
            return

        provider = self.provider_select.currentData()
        message_text = self._message_with_attachments(text)
        self.prompt_input.clear()
        self.sending = True
        self.send_button.setEnabled(False)
        self._append("user", text)
        self._append("system", "Thinking...")

        signals = WorkerSignals()
        self._send_signals = signals
        signals.message.connect(self._append)
        signals.tool_call.connect(self._append_tool_call)
        signals.usage.connect(self._append_usage)
        signals.error.connect(lambda msg: self._append("error", msg))
        signals.finished.connect(self._finish_send)

        def run():
            try:
                reply = self.chat.send(
                    message_text,
                    provider,
                    api_key,
                    self.model_input.currentText().strip() or settings.MODELS.get(provider, ""),
                    on_tool_call=lambda name, args: signals.tool_call.emit(name, json.dumps(args)),
                    on_usage=lambda usage: signals.usage.emit(usage),
                )
                signals.message.emit("assistant", reply or "(no reply)")
            except Exception as exc:
                signals.error.emit(str(exc))
            finally:
                signals.finished.emit()

        threading.Thread(target=run, daemon=True).start()

    def _message_with_attachments(self, text):
        if not self.attached_image_paths:
            return text

        paths = "\n".join(
            "{0}. {1}".format(index + 1, filepath)
            for index, filepath in enumerate(self.attached_image_paths)
        )
        return (
            "Attached reference image paths for local MCP tools:\n"
            "{0}\n\n"
            "When using Meshy image-to-3D, pass one of these paths as image_path.\n\n"
            "User request:\n{1}"
        ).format(paths, text)

    def _finish_send(self):
        self.sending = False
        self.send_button.setEnabled(self.connected)
        self._send_signals = None
        self._refresh_bridge_status()

    def _provider_changed(self):
        provider = self.provider_select.currentData()
        self.model_input.setCurrentText(settings.MODELS.get(provider, ""))
        self.load_models_button.setEnabled(provider == "openrouter")
        if self.chat:
            self.chat.reset(provider)
        self._append("system", "Provider changed. Conversation history reset for this provider.")

    def _append_tool_call(self, name, args_json):
        self.tool_log.append("<b>{0}</b><br><span>{1}</span><br>".format(
            self._escape(name),
            self._escape(args_json[:400]),
        ))
        self._refresh_bridge_status()

    def _append_usage(self, usage):
        if usage.get("summary"):
            self._append(
                "system",
                "Turn total ({0}, {1} call{2}): input {3:,}, output {4:,}, total {5:,}".format(
                    usage.get("provider", "llm"),
                    usage.get("calls", 0),
                    "" if usage.get("calls", 0) == 1 else "s",
                    usage.get("input_tokens", 0),
                    usage.get("output_tokens", 0),
                    usage.get("total_tokens", 0),
                ),
            )
            return

        self._append(
            "system",
            "Tokens ({0}): input {1:,}, output {2:,}, total {3:,}".format(
                usage.get("provider", "llm"),
                usage.get("input_tokens", 0),
                usage.get("output_tokens", 0),
                usage.get("total_tokens", 0),
            ),
        )

    def _show_available_tools(self):
        if not self.mcp or not self.mcp.tools:
            return

        names = [tool.get("name", "") for tool in self.mcp.tools]
        names = [name for name in names if name]
        self.tool_log.clear()
        self.tool_log.append("<b>Available MCP tools ({0})</b><br>".format(len(names)))
        self.tool_log.append("<br>".join(self._escape(name) for name in names))

    def _append(self, role, text):
        colors = {
            "user": ("#00d5f0", "#d8fbff"),
            "assistant": ("#54e285", "#e2ffe9"),
            "system": ("#87a4ff", "#dce6ff"),
            "error": ("#ff6b7a", "#ffe0e4"),
            "thinking": ("#c77dff", "#f4e3ff"),
        }
        label_color, text_color = colors.get(role, ("#9fb6bf", "#e7fbff"))
        html = (
            '<font color="{0}"><b>{1}</b></font><br>'
            '<font color="{2}">{3}</font><br><br>'
        ).format(
            label_color,
            self._escape(role),
            text_color,
            self._escape(text).replace("\n", "<br>"),
        )
        self.messages.append(html)

    @staticmethod
    def _escape(value):
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


_window = None


def show():
    global _window

    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])

    if _window is None:
        _window = NativeAssistantWindow(parent=get_main_window())
        _window.setObjectName("NativeAssistantWindow")

    _window.theme_name = apply_theme(_window)

    _window.show()
    _window.raise_()
    _window.activateWindow()
    return _window
