"""
    HelpWindow class
"""
from typing import Optional  # type: ignore
from overrides import override  # pylint: disable=import-error
from PySide6.QtWebEngineWidgets import QWebEngineView  # pylint: disable=import-error
from PySide6.QtGui import QCloseEvent  # pylint: disable=import-error
from PySide6.QtCore import QUrl, Slot  # pylint: disable=import-error
from PySide6.QtWidgets import QMainWindow  # pylint: disable=import-error

from IPTables_Guide.view.gui_utils import log_gui


class HelpWindow(QMainWindow):
    """
    Window displaying the help manual
    """

    _instance: Optional["HelpWindow"] = None

    def __init__(self) -> None:
        """ """
        assert HelpWindow._instance is None
        super().__init__()
        view = QWebEngineView(self)
        self.setCentralWidget(view)
        view.setUrl(QUrl("./index.html"))
        self.resize(600, 800)
        HelpWindow._instance = self
        assert log_gui("Help Window opened")

    @staticmethod
    def __instance_deleted():
        """
        Set instance to None
        """
        HelpWindow._instance = None

    @override
    def closeEvent(self, event: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
        handling close event
        """
        assert log_gui("Help Window closed")
        super().closeEvent(event)
        HelpWindow.__instance_deleted()
        self.deleteLater()

    @staticmethod
    def get_instance() -> "HelpWindow":
        """
        Returns the instance of this class

        If no intance is created, creates one
        """
        return HelpWindow._instance or HelpWindow()

    @staticmethod
    def delete_instance() -> None:
        """
        Deletes the only instance if exists
        """
        if HelpWindow._instance is not None:
            HelpWindow._instance.close()


@Slot()
def display_help() -> None:
    """
    Display the help manual
    """
    HelpWindow.get_instance().show()
    HelpWindow.get_instance().activateWindow()
