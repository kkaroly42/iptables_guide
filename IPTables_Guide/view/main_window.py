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
    QMessageBox,
)

from IPTables_Guide.view.help_window import HelpWindow, display_help
from IPTables_Guide.view.packete_window import PacketWindow, get_packet_window
from IPTables_Guide.view.iptable_window import IPTableWindow
from IPTables_Guide.view.persistence import PersistenceWindow
from IPTables_Guide.view.gui_utils import open_window, log_gui

from IPTables_Guide.model.rule_system import RuleSystem, Table


class MainWindow(QMainWindow):
    """
    main window of the project
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setCentralWidget(QWidget(self))

        self.model = RuleSystem()

        self.resize(300, 300)
        self.setWindowTitle("iptables guide")

        self.buttons = {
            "filter": QPushButton("Filter table", self.centralWidget()),
            "nat": QPushButton("Nat table", self.centralWidget()),
            "packages": QPushButton("Csomagküldés", self.centralWidget()),
            "persistence": QPushButton("Mentés/Betöltés", self.centralWidget()),
            "help": QPushButton("Súgó", self.centralWidget()),
        }

        self.setStyleSheet(
            """
            QMainWindow{
                background-color: #1C1C1E;
            }
            
                QPushButton {
                    background-color: #1C1C1E;
                    color: #BABBBE;
                    font-family: Consolas;
                    font-size: 20px;
                    padding: 6px 3px 6px 3px;
                    border: 1px solid #505054;
                    margin: 0px;
                }
                QPushButton:pressed{
                    background-color: #28282B;
                    color: #BABBBE;
                    border: 1px solid #28282B;
                }
                QPushButton:hover:!pressed {
                    background-color: #505054;
                    color: white;
                }
        """
        )

        self.main_layout: QVBoxLayout = QVBoxLayout()
        self.centralWidget().setLayout(self.main_layout)

        for k in ["filter", "nat", "packages", "persistence", "help"]:
            self.main_layout.addWidget(self.buttons[k])

        self.buttons["filter"].clicked.connect(  # type: ignore
            lambda: open_window(
                IPTableWindow, self, model=self.model, ip_table_type=Table.FILTER
            )
        )
        self.buttons["nat"].clicked.connect(  # type: ignore
            lambda: open_window(
                IPTableWindow, self, model=self.model, ip_table_type=Table.NAT
            )
        )
        self.buttons["packages"].clicked.connect(  # type: ignore
            # TODO handle packages
            lambda: get_packet_window(model=self.model)
        )
        self.buttons["persistence"].clicked.connect(  # type: ignore
            lambda: open_window(PersistenceWindow, self, model=self.model)
        )
        self.buttons["help"].clicked.connect(display_help)  # type: ignore

    @override
    def closeEvent(self, event: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
        handling close event
        """
        msgBox = QMessageBox()
        msgBox.setText("Menti kilépés előtt a módosításokat?")
        msgBox.setInformativeText("A nem mentett információk elvesznek")
        msgBox.setStandardButtons(
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        msgBox.setDefaultButton(QMessageBox.Save)
        ret = msgBox.exec()

        if ret == QMessageBox.Save:
            # Save was clicked
            open_window(PersistenceWindow, self, model=self.model)
        elif ret == QMessageBox.Discard:
            # Don't Save was clicked
            assert log_gui("Main Window close")
            HelpWindow.delete_instance()
            PacketWindow.delete_instance()
            super().closeEvent(event)
            event.accept()
        elif ret == QMessageBox.Cancel:
            # Cancel was clicked
            event.ignore()
        else:
            # should never be reached
            pass


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
