"""
    TableWindow representing an IPTable GUI
"""
import sys
from typing import Optional
from overrides import override  # pylint: disable=import-error

from PySide6.QtWidgets import (  # pylint: disable=import-error
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QRadioButton,
    QVBoxLayout,
)

from abstract_window import AbstractWindow
from chain_window import ChainWindow
from gui_utils import display_help, open_window


class IPTableWindow(AbstractWindow):
    """
        Window representing a table
    """

    def __init__(self, ip_table, parent: Optional[QWidget] = None) -> None:
        """
        """
        super().__init__(
            "",
            [
                ("select", QCheckBox),
                ("name", QLineEdit),
                ("open", QPushButton),
                ("statistics", QLineEdit),
            ],
            parent,
        )
        self.ip_table = ip_table

        self.buttons = []
        self.cathegory_widget = QWidget(self.menu_line)
        self.menu_line.layout().addWidget(self.cathegory_widget)
        self.menu_line.layout().insertStretch(-1)  # type: ignore

        self.buttons.append(QPushButton("New Chain", self.menu_line))
        self.buttons.append(QPushButton("Delete row", self.menu_line))
        self.buttons.append(QPushButton("Save", self.menu_line))
        self.buttons.append(QPushButton("Load", self.menu_line))
        self.buttons.append(QPushButton("Help", self.menu_line))
        for button in self.buttons:
            self.menu_line.layout().addWidget(button)
        self.buttons[0].clicked.connect(self.append_row)
        self.buttons[1].clicked.connect(self.delete_row)
        self.buttons[4].clicked.connect(display_help)

        self.cathegory_widget.setLayout(QVBoxLayout(self.cathegory_widget))

        self.cathegories = []
        self.cathegories.append(QRadioButton("Prerouting", self.cathegory_widget))
        self.cathegories.append(QRadioButton("Input", self.cathegory_widget))
        self.cathegories.append(QRadioButton("Forward", self.cathegory_widget))
        self.cathegories.append(QRadioButton("Output", self.cathegory_widget))
        self.cathegories.append(QRadioButton("Postrouting", self.cathegory_widget))
        for cathegory in self.cathegories:
            self.cathegory_widget.layout().addWidget(cathegory)
        self.cathegories[0].setChecked(True)

    @override
    def _set_row(self, ind: int):
        """
            config new row's behaviour
        """
        # TODO API call
        chain = None
        self.table[ind, "open"].clicked.connect(  # type: ignore
            lambda: open_window(ChainWindow, chain, self)
        )
        self.table[ind, "open"].setText("Modify")  # type: ignore
        # self.table.apply_method_to_row(ind, lambda w: w.setToolTip(chain.get_description()))


if __name__ == "__main__":
    app = QApplication([])
    window = IPTableWindow(None)
    window.show()
    sys.exit(app.exec())
