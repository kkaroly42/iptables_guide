"""
    TableWindow representing an IPTable GUI
"""
import sys
from typing import Optional, List
from overrides import override  # pylint: disable=import-error
from PySide6.QtCore import Slot  # pylint: disable=import-error


from PySide6.QtWidgets import (  # pylint: disable=import-error
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QRadioButton,
    QVBoxLayout,
    QMessageBox,
    QLabel,
)

from IPTables_Guide.view.abstract_table_window import AbstractTableWindow
from IPTables_Guide.view.gui_utils import log_gui
from IPTables_Guide.view.help_window import display_help

from IPTables_Guide.model.iptables import Iptables
from IPTables_Guide.model.rule_system import Table, Chain
from IPTables_Guide.model.rule_generator import Rule


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
            [("select", QCheckBox), ("rule", QLineEdit), ("check", QLabel)],
            parent,
        )

        if "kwargs" in kwargs:
            kwargs = kwargs["kwargs"]

        assert "model" in kwargs
        assert "ip_table_type" in kwargs

        self.ip_table_type: Table = kwargs["ip_table_type"]
        self.model: Iptables = kwargs["model"]

        self.setWindowTitle(self.ip_table_type.value.upper())

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

        self.buttons["new"].clicked.connect(self.append_clicked)  # type: ignore
        self.buttons["delete"].clicked.connect(self.delete_clicked)  # type: ignore
        self.buttons["insert"].clicked.connect(self.insert_clicked)  # type: ignore
        self.buttons["help"].clicked.connect(display_help)  # type: ignore

        self.chain_widget.setLayout(QVBoxLayout(self.chain_widget))

        self.chain_types: List = list(
            self.model._tables[self.ip_table_type.value].keys()
        )

        self.chain_radiobuttons = [
            QRadioButton(ct, self.chain_widget) for ct in self.chain_types
        ]

        for chain in self.chain_radiobuttons:
            chain.clicked.connect(self.setup_rules)  # type: ignore
            self.chain_widget.layout().addWidget(chain)
        self.chain_radiobuttons[0].setChecked(True)

        self.checked_value = self.chain_types[0]

        self.table_label.setText(
            "sudo iptables -L " + self.checked_value + " -t " + self.ip_table_type.value
        )
        for _ in self.model._tables[self.ip_table_type.value][self.chain_types[0]]:
            self.append_row()

        # TODO check Table and Chain
        self.model.rule_appended.connect(self.append_row)
        self.model.rule_inserted.connect(lambda x: self.insert_row(x))
        self.model.rule_deleted.connect(lambda x: self.delete_row(x))

    @override
    def _set_row(self, ind: int):
        """
        config new row's behaviour
        """
        # TODO API call instead of setting attribute
        self.table[ind, "rule"].setText(  # type: ignore
            self.model._tables[self.ip_table_type.value][self.checked_value][
                ind
            ].raw_form
        )
        self.table[ind, "check"].setText("")  # type: ignore
        # TODO check what differs
        def set_raw_form(text):
            self.model._tables[self.ip_table_type.value][self.checked_value][
                ind
            ].raw_form = text

        self.table[ind, "rule"].textEdited.connect(  # type: ignore
            lambda text: set_raw_form(text)
        )

    @Slot()
    def setup_rules(self) -> None:
        """
        Clear and display the rules in the chain
        """
        # clear the displayed rules
        assert isinstance(self.sender(), QRadioButton)
        text = self.sender().text()  # type: ignore
        log_gui("entered setup rules " + text)
        self.table.clear_table()
        self.checked_value = text
        for _ in self.model._tables[self.ip_table_type.value][self.checked_value]:
            self.append_row()
        self.table_label.setText(
            "sudo iptables -L " + self.checked_value + " -t " + self.ip_table_type.value
        )

    @staticmethod
    def __convert_to_chain(text: str) -> Chain:
        assert text.upper() in [e.value.upper() for e in Chain]
        for e in Chain:
            if e.value.upper() == text.upper():
                return e
        assert False

    @Slot()
    def append_clicked(self) -> None:
        # TODO pass table and chain as parameter
        self.model.append_rule(
            self.ip_table_type,
            self.__convert_to_chain(self.checked_value),
            Rule("", []),
        )

    @Slot()
    def insert_clicked(self) -> None:
        inds: List[int] = self._get_selected_indices()
        if len(inds) != 1:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Message")
            msg_box.setText("Insert is only enabled for exactly one row selected")
            msg_box.exec()
            return
        self.model.insert_rule(
            self.ip_table_type,
            self.__convert_to_chain(self.checked_value),
            Rule("", []),
            inds[0],
        )

    @Slot()
    def delete_clicked(self) -> None:
        inds: List[int] = self._get_selected_indices()
        for ind in inds:
            self.model.insert_rule(
                self.ip_table_type,
                self.__convert_to_chain(self.checked_value),
                Rule("", []),
                ind,
            )


if __name__ == "__main__":
    app = QApplication([])
    window = IPTableWindow(None)
    window.show()
    sys.exit(app.exec())
