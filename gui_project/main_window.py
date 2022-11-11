"""
    MainWindow class representing the main window of the program
"""
# This Python file uses the following encoding: utf-8
import sys
from typing import Optional
from overrides import override  # pylint: disable=import-error
from PySide6.QtGui import QCloseEvent  # pylint: disable=import-error
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
)

from gui_project.help_window import HelpWindow, display_help
from gui_project.packete_window import PacketeWindow, get_packete_window
from gui_project.iptable_window import IPTableWindow
from gui_project.persistence import PersistenceWindow
from gui_project.gui_utils import open_window, log_gui


class MainWindow(QMainWindow):
    """
        main window of the project
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setCentralWidget(QWidget(self))

        self.resize(300, 300)
        self.setWindowTitle("IPTable-Guide")

        self.buttons = {
            "filter": QPushButton("Filter table", self.centralWidget()),
            "nat": QPushButton("Nat table", self.centralWidget()),
            "packages": QPushButton("Edit packages", self.centralWidget()),
            "persistence": QPushButton("Save/Load", self.centralWidget()),
            "help": QPushButton("Help", self.centralWidget()),
        }

        self.main_layout: QVBoxLayout = QVBoxLayout()
        self.centralWidget().setLayout(self.main_layout)

        for k in ["filter", "nat", "packages", "persistence", "help"]:
            self.main_layout.addWidget(self.buttons[k])

        self.buttons["filter"].clicked.connect(  # type: ignore
            # TODO API call
            lambda: open_window(IPTableWindow, self, ip_table=None)
        )
        self.buttons["nat"].clicked.connect(  # type: ignore
            # TODO API call
            lambda: open_window(IPTableWindow, self, ip_table=None)
        )
        self.buttons["packages"].clicked.connect(  # type: ignore
            # TODO give the package manager as parameter
            lambda: get_packete_window(None)
        )
        self.buttons["persistence"].clicked.connect(  # type: ignore
            # TODO API call
            lambda: open_window(PersistenceWindow, self)
        )
        self.buttons["help"].clicked.connect(  # type: ignore
            display_help
        )

    @override
    def closeEvent(self, event: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
            handling close event
        """
        assert log_gui("Main Window close")
        HelpWindow.delete_instance()
        PacketeWindow.delete_instance()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
