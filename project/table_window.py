"""
    TableWindow representing an IPTable GUI
"""
import sys
from typing import Optional, List
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QLabel,
)

# from PySide6.QtWebEngineWidgets import QWebEngineView  # pylint: disable=import-error
from PySide6.QtCore import Slot  # , QUrl  # pylint: disable=import-error

from custom_table_widget import CustomTableWidget


class TableWindow(QMainWindow):
    """
        Window representing a table
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        """
        super().__init__(parent)
        self.setCentralWidget(QWidget(self))
        self.main_layout = QHBoxLayout()
        self.centralWidget().setLayout(self.main_layout)

        self.menu_line = QWidget(self.centralWidget())
        self.menu_line.setMaximumWidth(200)
        self.table = CustomTableWidget(
            [("select", QCheckBox), ("name", QLineEdit), ("statistics", QLineEdit)],
            self.centralWidget(),
        )

        self.main_layout.addWidget(self.menu_line)
        self.table_layout = QVBoxLayout()
        self.table_layout.addWidget(QLabel("", self.centralWidget()))
        self.table_layout.addWidget(self.table)
        self.table_layout.insertStretch(-1)
        self.main_layout.addLayout(self.table_layout)

        self.menu_line.setLayout(QVBoxLayout())

        self.buttons = []
        self.buttons.append(QPushButton("New Chain", self.menu_line))
        self.buttons.append(QPushButton("Delete row", self.menu_line))
        self.buttons.append(QPushButton("Save", self.menu_line))
        self.buttons.append(QPushButton("Load", self.menu_line))
        self.buttons.append(QPushButton("Help", self.menu_line))
        for button in self.buttons:
            self.menu_line.layout().addWidget(button)
        self.buttons[0].clicked.connect(self.append_row)
        self.buttons[1].clicked.connect(self.delete_row)

    def __get_selected_indices(self) -> List[int]:
        return [
            i
            for i, w in enumerate(self.table.get_column("select"))
            if w.isChecked()  # type: ignore
        ]

    @Slot()
    def append_row(self):
        """
            Append a row to the end of the table
        """
        # TODO call API first and wait for its signal
        self.table.add_row()

    @Slot()
    def insert_row(self):
        """
            Append a row to the end of the table
        """
        inds: List[int] = self.__get_selected_indices()
        if len(inds) != 1:
            return
        # TODO call API first and wait for its signal
        self.table.insert_row(inds[0])

    @Slot()
    def delete_row(self):
        """
            remove rows from table
        """
        # TODO call API first and wait for its signal
        del self.table[self.__get_selected_indices()]


if __name__ == "__main__":
    app = QApplication([])
    window = TableWindow()
    window.show()
    sys.exit(app.exec())
