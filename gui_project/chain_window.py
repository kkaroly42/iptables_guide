"""
    Representation of a Chain
"""

import sys
from typing import Optional  # type: ignore

from overrides import override  # pylint: disable=import-error
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QTextEdit,
)

from gui_project.abstract_table_window import AbstractTableWindow

# from gui_project.gui_utils import log_gui


class ChainWindow(AbstractTableWindow):
    """
        Window representing a table
    """

    def __init__(self, parent: Optional[QWidget] = None, **kwargs) -> None:
        """
            kwargs: chain
        """
        super().__init__(
            "",
            [("select", QCheckBox), ("type", QComboBox), ("other", QLineEdit)],
            parent,
        )
        # type: ignore
        self.chain = kwargs["chain"] if "chain" in kwargs else None
        # TODO get name of ip_table from API
        # self.setWindowTitle(chain.get_name())

        self.buttons = {}
        self.buttons["insert"] = QPushButton("Insert rule before", self.menu_line)
        self.buttons["append"] = QPushButton("Insert rule at the end", self.menu_line)
        self.buttons["delete"] = QPushButton("Delete rule", self.menu_line)
        self.description = QTextEdit(self.menu_line)
        for k in ["append", "insert", "delete"]:
            self.menu_line.layout().addWidget(self.buttons[k])
        self.buttons["insert"].clicked.connect(self.insert_row)  # type: ignore
        self.buttons["append"].clicked.connect(self.append_row)  # type: ignore
        self.buttons["delete"].clicked.connect(self.delete_row)  # type: ignore

        self.menu_line.layout().addWidget(self.description)

    @override
    def _set_row(self, ind: int) -> None:
        pass


if __name__ == "__main__":
    app = QApplication([])
    window = ChainWindow(None)
    window.show()
    sys.exit(app.exec())
