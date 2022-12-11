"""
Custom widgets derived from base QWidget types
"""
from overrides import override  # pylint: disable=import-error
from PySide6.QtCore import Signal, Qt  # pylint: disable=import-error
from PySide6.QtGui import QMouseEvent  # pylint: disable=import-error
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QWidget,
    QLineEdit,
)

from IPTables_Guide.view.gui_utils import log_gui
from IPTables_Guide.view.help_window import display_help


class CustomLineEdit(QLineEdit):
    """
    CustomLineEdit derived from QLineEdit

    overrides: mousePressEvent
    """

    modified_Right_clicked = Signal()
    """
    emited when CTRL + right mouse click happens
    """

    def __init__(self, parent: QWidget) -> None:
        """
        init
        """
        super().__init__(parent)

        self.setStyleSheet(
            """
            background-color: #2F2F32;
            border-color: #2F2F32;
            color: #BABBBE;
            font-family: Consolas;
            font-size: 16px;
            width: 250px;
            padding: 0 5px;
            margin: 2px;
        """
        )

    @override
    def mousePressEvent(self, arg__1: QMouseEvent) -> None:
        """
        handles mouse press on widget
        """
        if (
            arg__1.button() == Qt.MouseButton.RightButton
            and arg__1.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # TODO handle CTRL + right click
            assert log_gui("CTRL+right mouse button click happened")
            display_help()
            self.modified_Right_clicked.emit()
        super().mousePressEvent(arg__1)
