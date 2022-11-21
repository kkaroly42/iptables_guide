"""
    Persistence window
"""

from PySide6.QtCore import Slot  # pylint: disable=import-error
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QWidget,
    QMainWindow,
    QPushButton,
    QLineEdit,
    QGridLayout,
)

from IPTables_Guide.view.gui_utils import log_gui


class PersistenceWindow(QMainWindow):
    """
    Persistence Window
    """

    def __init__(self, parent: QWidget) -> None:
        """ """
        super().__init__(parent)

        self.setCentralWidget(QWidget(self))
        self.resize(600, 400)

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

    @Slot()
    def load_clicked(self):
        """
        Handle load
        """
        assert log_gui("Load clicked")
