"""
    Package manager window
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


class PackageType(Enum):
    """
        Enum for package types
    """

    TCP = "TCP"
    UDP = "UDP"


class CreatorDialog(QDialog):
    """
        dialog for creating a package
    """

    def __init__(self, parent: QWidget, package_type: Optional[PackageType] = None, package=None) -> None:
        super().__init__(parent)
        assert package or package_type
        if (package is not None) and (package_type is not None):
            # TODO check if the package_type is correct
            pass
        elif package is not None:
            # TODO set correct package_type
            pass

        self.package = package

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

        if package_type is PackageType.TCP:
            self.setWindowTitle("TCP package config")
            self.preferences.setPlainText(
                "from_adress=localhost\n"
                "from_port=10000\n"
                "to_adress=localhost\n"
                "to_port=10001\n"
                "package_size=10\n"
            )
        elif package_type is PackageType.UDP:
            self.setWindowTitle("UDP package config")
            self.preferences.setPlainText(
                "from_adress=localhost\n"
                "from_port=10000\n"
                "to_adress=localhost\n"
                "to_port=10001\n"
                "package_size=10\n"
            )
        else:
            assert False

    @override
    def closeEvent(self, arg__1: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
            handling close event
        """
        msg_box = QMessageBox()
        msg_box.setStandardButtons(
            QMessageBox.Ok | QMessageBox.Cancel)  # type: ignore
        msg_box.setText("Your changes wont be saved.")
        if msg_box.exec() is QMessageBox.Cancel:  # type: ignore
            arg__1.ignore()
            return
        assert log_gui("PackageWindow closed")
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
        if self.package is not None:
            # TODO set preferences
            pass
        self.accept()


class PackageWindow(AbstractTableWindow):
    """
        Window managing packages
    """

    _instance: Optional["PackageWindow"] = None

    def __init__(self, **kwargs) -> None:
        """
        """
        assert PackageWindow._instance is None
        super().__init__(
            "Packages",
            [("select", QCheckBox), ("name", QLineEdit), ("open", QPushButton), ],
        )
        self.package_manager = (
            kwargs["package_manager"] if "package_manager" in kwargs else None
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
            lambda: self.create_package(PackageType.TCP)
        )
        self.buttons["udp"].clicked.connect(  # type: ignore
            lambda: self.create_package(PackageType.UDP)
        )
        self.buttons["delete"].clicked.connect(self.delete_row)  # type: ignore

        PackageWindow._instance = self
        assert log_gui("PackageWindow opened")

    @Slot()
    def create_package(self, package_type: PackageType):
        """
            open a dialog with TCP template
        """
        dialog = CreatorDialog(self, package_type=package_type)
        dialog.accepted.connect(  # type: ignore
            lambda: self.add_package(
                package_type, dialog.preferences.toPlainText())
        )
        dialog.exec()

    @Slot()
    def modify_package(self, package):
        """
            open a dialog with TCP template
        """
        dialog = CreatorDialog(self, package=package)
        # TODO handle package modified
        dialog.accepted.connect(  # type: ignore
        )
        dialog.exec()

    def add_package(self, package_type: PackageType, preferences: str) -> None:
        """
        """
        # TODO API calls
        self.append_row()

    @override
    def _set_row(self, ind: int) -> None:
        package=None
        self.table[ind, "open"].clicked.connect(  # type: ignore
            # TODO handle package
            lambda: self.modify_package(package)
        )
        self.table[ind, "open"].setText("Modify")  # type: ignore

    @staticmethod
    def __instance_deleted():
        """
            Set instance to None
        """
        PackageWindow._instance = None

    @override
    def closeEvent(self, event: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
            handling close event
        """
        assert log_gui("PackageWindow closed")
        super().closeEvent(event)
        PackageWindow.__instance_deleted()
        self.deleteLater()

    @staticmethod
    def get_instance(package_manager: Optional[Any] = None) -> "PackageWindow":
        """
            Returns the instance of this class

            If no intance is created, creates one
        """
        assert (package_manager is None) or (PackageWindow._instance is None)
        return PackageWindow._instance or PackageWindow(package_manager=package_manager)

    @staticmethod
    def delete_instance() -> None:
        """
            Deletes the only instance if exists
        """
        if PackageWindow._instance is not None:
            PackageWindow._instance.close()


@Slot()
def get_package_window(package_manager) -> None:
    """
        Display the package manager
    """
    package_manager = package_manager if PackageWindow._instance is None else None
    PackageWindow.get_instance(package_manager).show()
    PackageWindow.get_instance().activateWindow()
