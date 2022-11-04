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

from gui_project.abstract_table_window import AbstractTableWindow
from gui_project.chain_window import ChainWindow
from gui_project.gui_utils import open_window
from gui_project.help_window import display_help


class IPTableWindow(AbstractTableWindow):
    """
        Window representing a table
    """

    def __init__(self, parent: Optional[QWidget] = None, **kwargs) -> None:
        """
            kwargs: ip_table
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
        # TODO get name of ip_table from API
        # self.setWindowTitle(ip_table.get_name())
        self.ip_table = kwargs["ip_table"] if "ip_table" in kwargs else None

        self.buttons = {}
        self.cathegory_widget = QWidget(self.menu_line)
        self.menu_line.layout().addWidget(self.cathegory_widget)
        self.menu_line.layout().insertStretch(-1)  # type: ignore

        self.buttons["new"] = QPushButton("New Chain", self.menu_line)
        self.buttons["delete"] = QPushButton("Delete row", self.menu_line)
        self.buttons["help"] = QPushButton("Help", self.menu_line)
        for k in ["new", "delete", "help"]:
            self.menu_line.layout().addWidget(self.buttons[k])
        self.buttons["new"].clicked.connect(self.append_row)  # type: ignore
        self.buttons["delete"].clicked.connect(self.delete_row)  # type: ignore
        self.buttons["help"].clicked.connect(display_help)  # type: ignore

        self.cathegory_widget.setLayout(QVBoxLayout(self.cathegory_widget))

        # TODO get from ip_table
        self.cathegory_types = [
            "Prerouting",
            "Input",
            "Forward",
            "Output",
            "Postrouting",
        ]
        self.cathegory_buttons = [
            QRadioButton(ct, self.cathegory_widget) for ct in self.cathegory_types
        ]
        for cathegory in self.cathegory_buttons:
            self.cathegory_widget.layout().addWidget(cathegory)
        self.cathegory_buttons[0].setChecked(True)

    @override
    def _set_row(self, ind: int):
        """
            config new row's behaviour
        """
        # TODO API call
        chain = None
        self.table[ind, "open"].clicked.connect(  # type: ignore
            lambda: open_window(ChainWindow, self, chain=chain)
        )
        self.table[ind, "open"].setText("Modify")  # type: ignore
        # self.table.apply_method_to_row(ind, lambda w: w.setToolTip(chain.get_description()))


if __name__ == "__main__":
    app = QApplication([])
    window = IPTableWindow(None)
    window.show()
    sys.exit(app.exec())
