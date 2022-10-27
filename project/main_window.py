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

from help_window import HelpWindow
from table_window import IPTableWindow
from gui_utils import display_help, open_window


class MainWindow(QMainWindow):
    """
        main window of the project
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setCentralWidget(QWidget(self))

        self.buttons = {
            "filter": QPushButton("Filter table", self.centralWidget()),
            "nat": QPushButton("Nat table", self.centralWidget()),
            "packages": QPushButton("Edit packages", self.centralWidget()),
            "help": QPushButton("Help", self.centralWidget()),
        }

        self.main_layout: QVBoxLayout = QVBoxLayout()
        self.centralWidget().setLayout(self.main_layout)

        for button in self.buttons.values():
            self.main_layout.addWidget(button)

        self.buttons["filter"].clicked.connect(  # type: ignore
            # TODO API call
            lambda: open_window(IPTableWindow, None, self)
        )
        self.buttons["nat"].clicked.connect(  # type: ignore
            # TODO API call
            lambda: open_window(IPTableWindow, None, self)
        )
        self.buttons["help"].clicked.connect(  # type: ignore
            display_help
        )

    @override
    def closeEvent(self, event: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
            handling close event
        """
        HelpWindow.delete_instance()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
