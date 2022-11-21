"""
    TableWindow representing an IPTable GUI
"""
import sys
from typing import Optional
from overrides import override  # pylint: disable=import-error
from PySide6.QtCore import Slot  # pylint: disable=import-error


from PySide6.QtWidgets import (  # pylint: disable=import-error
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QRadioButton,
    QComboBox,
    QVBoxLayout,
    QTextEdit,
)

from IPTables_Guide.view.abstract_table_window import AbstractTableWindow
from IPTables_Guide.view.gui_utils import log_gui
from IPTables_Guide.view.help_window import display_help


class IPTableWindow(AbstractTableWindow):
    """
    Window for editing chains and rules
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
                ("type", QComboBox),
                ("statistics", QLineEdit),
            ],
            parent,
        )
        # TODO get name of ip_table from API
        # self.setWindowTitle(ip_table.get_name())
        self.ip_table = kwargs["ip_table"] if "ip_table" in kwargs else None

        self.setStyleSheet(
            """
            background-color: #1C1C1E;
            color: #BABBBE;
            font-family: Consolas;
            font-size: 16px;
        """
        )

        self.buttons = {}
        self.chain_widget = QWidget(self.menu_line)
        self.menu_line.layout().addWidget(self.chain_widget)
        self.menu_line.layout().insertStretch(-1)  # type: ignore

        self.menu_line.setStyleSheet(
            """
            background-color: #2F2F32;
            color: #A2D5AC;
        """
        )

        # self.description = QTextEdit(self.menu_line)
        # self.description.setReadOnly(True)
        # TODO get the description
        # self.menu_line.layout().addWidget(self.description)

        self.buttons["new"] = QPushButton("hozzáadás", self.menu_line)
        self.buttons["delete"] = QPushButton("törlés", self.menu_line)
        self.buttons["insert"] = QPushButton("beszúrás elé", self.menu_line)
        self.buttons["help"] = QPushButton("súgó", self.menu_line)

        for k in ["new", "delete", "insert", "help"]:
            self.buttons[k].setStyleSheet(
                """
                color: #BABABE;
            """
            )
            self.menu_line.layout().addWidget(self.buttons[k])

        self.buttons["new"].clicked.connect(self.append_row)  # type: ignore
        self.buttons["delete"].clicked.connect(self.delete_row)  # type: ignore
        self.buttons["insert"].clicked.connect(self.insert_row)  # type: ignore
        self.buttons["help"].clicked.connect(display_help)  # type: ignore

        self.chain_widget.setLayout(QVBoxLayout(self.chain_widget))

        # TODO get from ip_table
        self.chain_types = [
            "PREROUTING",
            "INPUT",
            "FORWARD",
            "OUTPUT",
            "POSTROUTING",
        ]
        self.chain_radiobuttons = [
            QRadioButton(ct, self.chain_widget) for ct in self.chain_types
        ]
        for chain in self.chain_radiobuttons:
            chain.clicked.connect(lambda: self.setup_rules(chain.text()))  # type: ignore
            self.chain_widget.layout().addWidget(chain)
        self.chain_radiobuttons[0].setChecked(True)

    @override
    def _set_row(self, ind: int):
        """
        config new row's behaviour
        """
        # TODO API call
        chain = None
        # self.table[ind, "open"].clicked.connect(  # type: ignore
        #  lambda: open_window(ChainWindow, self, chain=chain)
        # )
        self.table[ind, "name"].setReadOnly(True)  # type: ignore
        self.table[ind, "open"].setText("Modify")  # type: ignore
        # self.table.apply_method_to_row(ind, lambda w: w.setToolTip(chain.get_description()))

    @Slot()
    def setup_rules(self, text: str) -> None:
        """
        Clear and display the rules in the chain
        """
        # TODO get the rules from the model by the name of the chain (text)
        # TODO display the rules
        # clear the displayed rules
        log_gui("entered setup rules")
        self.table.clear_table()


if __name__ == "__main__":
    app = QApplication([])
    window = IPTableWindow(None)
    window.show()
    sys.exit(app.exec())
