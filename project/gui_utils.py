"""
    Utils for GUI
"""
from typing import Optional
from PySide6.QtCore import Slot, QEventLoop  # pylint: disable=import-error
from PySide6.QtWidgets import QMainWindow  # pylint: disable=import-error

from help_window import HelpWindow


@Slot()
def display_help():
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
    if parent is not None:
        parent.setEnabled(False)
    window = window_type(param, parent)
    window.show()
    # TODO fix modality
    # window.setWindowModality(Qt.WindowModal)  # type: ignore
    event_loop = QEventLoop()
    window.destroyed.connect(event_loop.quit)  # type: ignore
    event_loop.exec()
    if parent is not None:
        parent.setEnabled(True)
