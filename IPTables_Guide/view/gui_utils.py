"""
    Utils for GUI
"""
import time
from dataclasses import dataclass
from typing import Optional, Literal, Callable
from PySide6.QtCore import Slot, QEventLoop, Qt  # type: ignore # pylint: disable=import-error type: ignore
from PySide6.QtWidgets import QMainWindow, QPushButton  # type: ignore # pylint: disable=import-error


@dataclass
class Button:
    btn: QPushButton
    call: Callable


@Slot()
def open_window(window_type: type, parent: Optional[QMainWindow], **kwargs) -> None:
    """
    Opens a new IPTableWindow and wait until it closes
    """
    if len(kwargs) > 0:
        window = window_type(parent=parent, kwargs=kwargs)
    else:
        window = window_type(parent=parent)
    assert log_gui(f"{type(window)} opened")
    window.setWindowModality(Qt.WindowModal)  # type: ignore
    window.show()

    # wait until the child window closes
    # the child window must call deleteLater after close
    event_loop = QEventLoop()
    window.destroyed.connect(event_loop.quit)  # type: ignore
    event_loop.exec()

    assert log_gui(f"{type(window)} closed")
    # only the top window can be editable
    if parent is not None:
        parent.setWindowModality(Qt.WindowModal)  # type: ignore


def log_gui(msg: str) -> Literal[True]:
    """
    Log Gui events to stdout
    """
    print(f"<{time.ctime()}> log: {msg}")
    return True
