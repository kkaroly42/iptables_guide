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

from IPTables_Guide.view.abstract_table_window import AbstractTableWindow
from IPTables_Guide.view.chain_window import ChainWindow
from IPTables_Guide.view.gui_utils import open_window
from IPTables_Guide.view.help_window import display_help


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

        self.buttons["help"] = QPushButton("Help", self.menu_line)
        for k in ["help"]:
            self.menu_line.layout().addWidget(self.buttons[k])
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
        for cathegory in self.cathegory_types:
            self.append_row()
            self.table[-1, "name"].setText(cathegory)  # type: ignore

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
        self.table[ind, "name"].setReadOnly(True)  # type: ignore
        self.table[ind, "open"].setText("Modify")  # type: ignore
        # self.table.apply_method_to_row(ind, lambda w: w.setToolTip(chain.get_description()))


if __name__ == "__main__":
    app = QApplication([])
    window = IPTableWindow(None)
    window.show()
    sys.exit(app.exec())
