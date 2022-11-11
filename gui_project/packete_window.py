"""
    Packete manager window
"""

from typing import Optional, Any, List
from enum import Enum
from overrides import override  # pylint: disable=import-error

from PySide6.QtCore import Slot  # pylint: disable=import-error
from PySide6.QtGui import QCloseEvent  # pylint: disable=import-error
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QWidget,
    QMessageBox,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QDialog,
    QPlainTextEdit,
    QVBoxLayout,
    QHBoxLayout,
)

from gui_project.abstract_table_window import AbstractTableWindow
from gui_project.gui_utils import log_gui


class PacketeType(Enum):
    """
        Enum for packete types
    """

    TCP = "TCP"
    UDP = "UDP"


class CreatorDialog(QDialog):
    """
        dialog for creating a packete
    """

    def __init__(
        self, parent: QWidget, packete_type: Optional[PacketeType] = None, packete=None
    ) -> None:
        super().__init__(parent)
        assert packete or packete_type
        if (packete is not None) and (packete_type is not None):
            # TODO check if the packete_type is correct
            pass
        elif packete is not None:
            # TODO set correct packete_type
            pass

        self.packete = packete

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.preferences = QPlainTextEdit(self)
        self.main_layout.addWidget(self.preferences)

        self.return_layout = QHBoxLayout()
        self.main_layout.addLayout(self.return_layout)

        self.accept_button = QPushButton("Apply", self)
        self.reject_button = QPushButton("Cancel", self)

        self.return_layout.addWidget(self.accept_button)
        self.return_layout.addWidget(self.reject_button)

        self.accept_button.clicked.connect(self.added)  # type: ignore
        self.reject_button.clicked.connect(self.close)  # type: ignore

        if packete_type is PacketeType.TCP:
            self.setWindowTitle("TCP packete config")
            self.preferences.setPlainText(
                "from_adress=localhost\n"
                "from_port=10000\n"
                "to_adress=localhost\n"
                "to_port=10001\n"
                "packete_size=10\n"
            )
        elif packete_type is PacketeType.UDP:
            self.setWindowTitle("UDP packete config")
            self.preferences.setPlainText(
                "from_adress=localhost\n"
                "from_port=10000\n"
                "to_adress=localhost\n"
                "to_port=10001\n"
                "packete_size=10\n"
            )
        else:
            assert False

    @override
    def closeEvent(self, arg__1: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
            handling close event
        """
        msg_box = QMessageBox()
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # type: ignore
        msg_box.setText("Your changes wont be saved.")
        ret: int = msg_box.exec()
        if ret == QMessageBox.Cancel:  # type: ignore
            arg__1.ignore()
            return
        assert log_gui("PacketeWindow closed")
        # TODO
        super().closeEvent(arg__1)

    @Slot()
    def added(self):
        """
            handle if the user choiced add

            check if the given text has a valid format
        """
        line: str = self.preferences.toPlainText()
        line = line.replace("\r", "").replace(" ", "").replace("\t", "")
        lines: List[str] = line.split("\n")
        lines = [l for l in lines if l != ""]
        if any(l.count("=") != 1 for l in lines):
            msg_box = QMessageBox()
            msg_box.setText("A line must contain exactly 1 '='")
            msg_box.exec()
            return
        if self.packete is not None:
            # TODO set preferences
            pass
        self.accept()


class PacketeWindow(AbstractTableWindow):
    """
        Window managing packetes
    """

    _instance: Optional["PacketeWindow"] = None

    def __init__(self, **kwargs) -> None:
        """
        """
        assert PacketeWindow._instance is None
        super().__init__(
            "Packetes",
            [("select", QCheckBox), ("name", QLineEdit), ("open", QPushButton),],
        )
        self.packete_manager = (
            kwargs["packete_manager"] if "packete_manager" in kwargs else None
        )
        self.resize(600, 400)

        self.buttons = {}

        self.buttons["tcp"] = QPushButton("TCP template", self.centralWidget())
        self.buttons["udp"] = QPushButton("UDP template", self.centralWidget())
        self.buttons["delete"] = QPushButton("Delete", self.centralWidget())

        for key in ["tcp", "udp", "delete"]:
            self.menu_line.layout().addWidget(self.buttons[key])

        self.menu_line.layout().insertStretch(-1)  # type: ignore

        self.buttons["tcp"].clicked.connect(  # type: ignore
            lambda: self.create_packete(PacketeType.TCP)
        )
        self.buttons["udp"].clicked.connect(  # type: ignore
            lambda: self.create_packete(PacketeType.UDP)
        )
        self.buttons["delete"].clicked.connect(self.delete_row)  # type: ignore

        PacketeWindow._instance = self
        assert log_gui("PacketeWindow opened")

    @Slot()
    def create_packete(self, packete_type: PacketeType):
        """
            open a dialog with TCP template
        """
        dialog = CreatorDialog(self, packete_type=packete_type)
        dialog.accepted.connect(  # type: ignore
            lambda: self.add_packete(packete_type, dialog.preferences.toPlainText())
        )
        dialog.exec()

    @Slot()
    def modify_packete(self, packete):
        """
            open a dialog with TCP template
        """
        dialog = CreatorDialog(self, packete=packete)
        # TODO handle packete modified
        dialog.accepted.connect()  # type: ignore
        dialog.exec()

    def add_packete(self, packete_type: PacketeType, preferences: str) -> None:
        """
        """
        # TODO API calls
        self.append_row()

    @override
    def _set_row(self, ind: int) -> None:
        packete = None
        self.table[ind, "open"].clicked.connect(  # type: ignore
            # TODO handle packete
            lambda: self.modify_packete(packete)
        )
        self.table[ind, "open"].setText("Modify")  # type: ignore

    @staticmethod
    def __instance_deleted():
        """
            Set instance to None
        """
        PacketeWindow._instance = None

    @override
    def closeEvent(self, event: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
            handling close event
        """
        assert log_gui("PacketeWindow closed")
        super().closeEvent(event)
        PacketeWindow.__instance_deleted()
        self.deleteLater()

    @staticmethod
    def get_instance(packete_manager: Optional[Any] = None) -> "PacketeWindow":
        """
            Returns the instance of this class

            If no intance is created, creates one
        """
        assert (packete_manager is None) or (PacketeWindow._instance is None)
        return PacketeWindow._instance or PacketeWindow(packete_manager=packete_manager)

    @staticmethod
    def delete_instance() -> None:
        """
            Deletes the only instance if exists
        """
        if PacketeWindow._instance is not None:
            PacketeWindow._instance.close()


@Slot()
def get_packete_window(packete_manager) -> None:
    """
        Display the packete manager
    """
    packete_manager = packete_manager if PacketeWindow._instance is None else None
    PacketeWindow.get_instance(packete_manager).show()
    PacketeWindow.get_instance().activateWindow()
