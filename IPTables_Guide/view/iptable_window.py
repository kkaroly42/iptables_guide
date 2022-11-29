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

from IPTables_Guide.model.rule_system import Table, RuleSystem


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

        kwargs = kwargs.get("kwargs", kwargs)

        assert "model" in kwargs
        assert "ip_table_type" in kwargs

        self.ip_table_type: Table = kwargs["ip_table_type"]
        self.model: RuleSystem = kwargs["model"]

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

        self.chain_types: List = self.model.get_chain_names(self.ip_table_type)

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
        for _ in self.model.get_rules_in_chain(self.ip_table_type, self.checked_value):
            self.append_row()

        self.model.rule_appended.connect(self.rule_appended)
        self.model.rule_inserted.connect(self.rule_inserted)
        self.model.rule_deleted.connect(self.rule_deleted)

    @Slot(str, str)
    def rule_appended(self, table_str: str, chain_str: str) -> None:
        """
        handle model rule_appended
        """
        assert log_gui(f"Rule appended recived: {table_str} {chain_str}")
        if self.ip_table_type.value == table_str and self.checked_value == chain_str:
            self.append_row()
        else:
            assert False

    @Slot(str, str, int)
    def rule_inserted(self, table_str: str, chain_str: str, ind: int) -> None:
        """
        handle model rule_inserted
        """
        assert log_gui(f"Rule inserted recived: {table_str} {chain_str} {ind}")
        if self.ip_table_type.value == table_str and self.checked_value == chain_str:
            self.insert_row(ind)
        else:
            assert False

    @Slot(str, str, int)
    def rule_deleted(self, table_str: str, chain_str: str, ind: int) -> None:
        """
        handle model rule_deleted
        """
        assert log_gui(f"Rule inserted recived: {table_str} {chain_str} {ind}")
        if self.ip_table_type.value == table_str and self.checked_value == chain_str:
            self.delete_row(ind)
        else:
            assert False

    @override
    def _set_row(self, ind: int):
        """
        config new row's behaviour
        """
        # TODO API call instead of setting attribute
        self.table[ind, "rule"].setText(  # type: ignore
            self.model.get_rule(
                self.ip_table_type, self.checked_value, ind
            ).get_str_form()
        )
        self.table[ind, "check"].setText("")  # type: ignore
        self.table[ind, "rule"].textEdited.connect(  # type: ignore
            lambda text: self.model.update_rule(
                self.ip_table_type,
                self.checked_value,
                ind,
                text,
            )
        )
        # TODO set label based on checks

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
        for _ in self.model.get_rules_in_chain(self.ip_table_type, self.checked_value):
            self.append_row()
        self.table_label.setText(
            "sudo iptables -L " + self.checked_value + " -t " + self.ip_table_type.value
        )

    @Slot()
    def append_clicked(self) -> None:
        """
        handle append clicked
        """
        self.model.append_rule(
            self.ip_table_type,
            self.checked_value,
            self.model.create_rule_from_raw_str(
                "", self.ip_table_type, self.checked_value
            ),
        )

    @Slot()
    def insert_clicked(self) -> None:
        """
        handle insert clicked
        """
        inds: List[int] = self._get_selected_indices()
        if len(inds) != 1:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Message")
            msg_box.setText("Insert is only enabled for exactly one row selected")
            msg_box.exec()
            return
        self.model.insert_rule(
            self.ip_table_type,
            self.checked_value,
            self.model.create_rule_from_raw_str(
                "", self.ip_table_type, self.checked_value
            ),
            inds[0],
        )

    @Slot()
    def delete_clicked(self) -> None:
        """
        handle delete clicked
        """
        inds: List[int] = self._get_selected_indices()
        inds.sort()
        inds.reverse()
        for ind in inds:
            self.model.delete_rule(self.ip_table_type, self.checked_value, ind)


if __name__ == "__main__":
    app = QApplication([])
    window = IPTableWindow(None)
    window.show()
    sys.exit(app.exec())
