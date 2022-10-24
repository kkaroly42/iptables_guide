"""
    Representation of a Chain
"""

import sys
from typing import Optional, List
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QTextEdit,
)

from PySide6.QtCore import Slot  # pylint: disable=import-error

from abstract_window import AbstractWindow


class ChainWindow(AbstractWindow):
    """
        Window representing a table
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        """
        super().__init__(
            "",
            [("select", QCheckBox), ("type", QComboBox), ("other", QLineEdit)],
            parent,
        )

        self.buttons = []
        self.buttons.append(QPushButton("Insert rule before", self.menu_line))
        self.buttons.append(QPushButton("insert rule at the end", self.menu_line))
        self.buttons.append(QPushButton("Delete rule", self.menu_line))
        self.buttons.append(QTextEdit(self.menu_line))
        for button in self.buttons:
            self.menu_line.layout().addWidget(button)
        self.buttons[0].clicked.connect(self.insert_row)
        self.buttons[1].clicked.connect(self.append_row)
        self.buttons[2].clicked.connect(self.delete_row)

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
        inds: List[int] = self._get_selected_indices()
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
        del self.table[self._get_selected_indices()]


if __name__ == "__main__":
    app = QApplication([])
    window = ChainWindow()
    window.show()
    sys.exit(app.exec())
