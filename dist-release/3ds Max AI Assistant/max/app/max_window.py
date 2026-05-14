try:
    from PySide2 import QtWidgets
    import shiboken2
except ImportError:
    from PySide6 import QtWidgets
    import shiboken6 as shiboken2


def get_main_window():
    qtmax_window = _get_window_from_qtmax()
    if qtmax_window:
        return qtmax_window

    handle = _get_main_window_handle()
    if not handle:
        return None
    return shiboken2.wrapInstance(int(handle), QtWidgets.QWidget)


def _get_main_window_handle():
    handle = _get_handle_from_maxplus()
    if handle:
        return handle

    handle = _get_handle_from_windows_api()
    if handle:
        return handle

    return None


def _get_window_from_qtmax():
    try:
        import qtmax

        return qtmax.GetQMaxMainWindow()
    except Exception:
        return None


def _get_handle_from_maxplus():
    try:
        import MaxPlus

        return MaxPlus.Win32.GetMAXHWnd()
    except Exception:
        return None


def _get_handle_from_windows_api():
    try:
        import ctypes

        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        buffer = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buffer, 512)
        if "3ds Max" in buffer.value or "Autodesk" in buffer.value:
            return hwnd
    except Exception:
        return None

    return None
