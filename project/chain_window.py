"""
    Representation of a Chain
"""

import sys
from typing import Optional  # type: ignore
from overrides import override  # pylint: disable=import-error
from PySide6.QtCore import Qt  # pylint: disable=import-error
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QTextEdit,
)

from abstract_window import AbstractWindow


class ChainWindow(AbstractWindow):
    """
        Window representing a table
    """

    def __init__(self, chain, parent: Optional[QWidget] = None) -> None:
        """
        """
        super().__init__(
            "",
            [("select", QCheckBox), ("type", QComboBox), ("other", QLineEdit)],
            parent,
        )
        self.chain = chain

        self.setWindowModality(Qt.WindowModal)  # type: ignore

        self.buttons = []
        self.buttons.append(QPushButton("Insert rule before", self.menu_line))
        self.buttons.append(QPushButton("Insert rule at the end", self.menu_line))
        self.buttons.append(QPushButton("Delete rule", self.menu_line))
        self.description = QTextEdit(self.menu_line)
        for button in self.buttons:
            self.menu_line.layout().addWidget(button)
        self.buttons[0].clicked.connect(self.insert_row)
        self.buttons[1].clicked.connect(self.append_row)
        self.buttons[2].clicked.connect(self.delete_row)

        self.menu_line.layout().addWidget(self.description)

    @override
    def _set_row(self, ind: int) -> None:
        pass


if __name__ == "__main__":
    app = QApplication([])
    window = ChainWindow(None)
    window.show()
    sys.exit(app.exec())
