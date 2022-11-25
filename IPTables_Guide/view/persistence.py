"""
    Persistence window
"""

import os

from PySide6.QtCore import Slot  # pylint: disable=import-error
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QWidget,
    QMainWindow,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QMessageBox,
)

from IPTables_Guide.view.gui_utils import log_gui

from IPTables_Guide.model.rule_system import RuleSystem


class PersistenceWindow(QMainWindow):
    """
    Persistence Window
    """

    def __init__(self, parent: QWidget, **kwargs) -> None:
        """ """
        super().__init__(parent)

        kwargs = kwargs.get("kwargs", kwargs)

        self.model: RuleSystem = kwargs["model"]

        self.setCentralWidget(QWidget(self))
        self.resize(600, 400)
        self.setWindowTitle("Mentés / Betöltés")

        self.file_name_edit = QLineEdit(self.centralWidget())

        self.save_button = QPushButton("Save", self.centralWidget())
        self.load_button = QPushButton("Load", self.centralWidget())

        self.main_layout = QGridLayout()

        self.centralWidget().setLayout(self.main_layout)

        self.main_layout.addWidget(self.file_name_edit, 0, 0, 1, 2)
        self.main_layout.addWidget(self.save_button, 1, 0)
        self.main_layout.addWidget(self.load_button, 1, 1)

        self.save_button.clicked.connect(self.save_clicked)  # type: ignore
        self.load_button.clicked.connect(self.load_clicked)  # type: ignore

    @Slot()
    def save_clicked(self):
        """
        Handle save
        """
        assert log_gui("Save clicked")
        file_name = self.file_name_edit.text()
        if (
            sum(
                file_name.count(c)
                for c in ["/", "\\", "|", "<", ">", ":", '"', "?", "*"]
            )
            == 0
        ):
            self.model.write_to_file(file_name)
        else:
            msg_box = QMessageBox()
            msg_box.setText(f"A megadott fájlnév nem valid: {file_name}")
            msg_box.exec()

    @Slot()
    def load_clicked(self):
        """
        Handle load
        """
        assert log_gui("Load clicked")
        file_name = self.file_name_edit.text()
        if os.path.isfile(file_name):
            self.model.read_from_file(file_name)
        else:
            msg_box = QMessageBox()
            msg_box.setText(f"A megadott fájlnév nem valid: {file_name}")
            msg_box.exec()
