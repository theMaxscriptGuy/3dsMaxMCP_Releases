def apply_theme(widget):
    try:
        from qt_material import build_stylesheet

        widget.setStyleSheet(build_stylesheet(theme="dark_cyan.xml"))
        return "qt-material dark_cyan"
    except Exception:
        widget.setStyleSheet(DARK_CYAN_STYLESHEET)
        return "built-in dark cyan"


DARK_CYAN_STYLESHEET = """
QDialog {
    background: #101418;
    color: #d7edf0;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 10pt;
}

QLabel {
    color: #a9c9ce;
}

QLineEdit,
QPlainTextEdit,
QTextEdit,
QComboBox {
    background: #151c22;
    color: #e7fbff;
    border: 1px solid #263840;
    border-radius: 4px;
    padding: 6px;
    selection-background-color: #00acc1;
    selection-color: #071114;
}

QTextEdit {
    line-height: 1.35;
}

QTextEdit#messages,
QTextEdit#toolLog {
    background: #0d1216;
}

QLabel#portStatus {
    color: #64d8e8;
}

QLineEdit:focus,
QPlainTextEdit:focus,
QTextEdit:focus,
QComboBox:focus {
    border: 1px solid #00bcd4;
}

QPushButton {
    background: #008fa1;
    color: #f1feff;
    border: 1px solid #00bcd4;
    border-radius: 4px;
    padding: 7px 12px;
    font-weight: 600;
}

QPushButton:hover {
    background: #00a7bb;
}

QPushButton:pressed {
    background: #007b8a;
}

QPushButton:disabled {
    background: #253138;
    border-color: #34464f;
    color: #71878d;
}

QSplitter::handle {
    background: #1d2a31;
}

QScrollBar:vertical,
QScrollBar:horizontal {
    background: #101418;
    border: none;
    margin: 0;
}

QScrollBar::handle {
    background: #31454e;
    border-radius: 4px;
    min-height: 22px;
}

QScrollBar::handle:hover {
    background: #00a7bb;
}
"""
