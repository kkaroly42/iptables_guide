"""
    Utils for GUI
"""
from typing import Optional
from PySide6.QtCore import Slot, QEventLoop, Qt  # pylint: disable=import-error
from PySide6.QtWidgets import QMainWindow  # pylint: disable=import-error

from gui_project.help_window import HelpWindow


@Slot()
def display_help() -> None:
    """
        Display the help manual
    """
    HelpWindow.get_instance().show()
    HelpWindow.get_instance().activateWindow()


@Slot()
def open_window(window_type: type, param, parent: Optional[QMainWindow]) -> None:
    """
        Opens a new IPTableWindow and wait until it closes
    """
    window = window_type(param, parent)
    window.setWindowModality(Qt.WindowModal)  # type: ignore
    window.show()

    # wait until the child window closes
    # the child window must call deleteLater after close
    event_loop = QEventLoop()
    window.destroyed.connect(event_loop.quit)  # type: ignore
    event_loop.exec()

    # only the top window can be editable
    if parent is not None:
        parent.setWindowModality(Qt.WindowModal)  #  type: ignore
