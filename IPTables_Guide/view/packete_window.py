"""
    Packet manager window
"""
from __future__ import annotations
import os
from typing import Optional, Any, List
from overrides import override  # pylint: disable=import-error

# from IPTables_Guide.model.rule_generator import Rule
from PySide6.QtCore import Slot  # pylint: disable=import-error
from PySide6.QtGui import QCloseEvent  # pylint: disable=import-error
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QWidget,
    QMessageBox,
    QPushButton,
    QLineEdit,
    QComboBox,
    QLabel,
    QGridLayout,
)

from IPTables_Guide.view.abstract_table_window import AbstractTableWindow
from IPTables_Guide.view.gui_utils import log_gui

from IPTables_Guide.model.packets import PacketType, Packet
from IPTables_Guide.model.rule_system import RuleSystem


class PacketWindow(QWidget):
    """"""

    instance: Optional[PacketWindow] = None

    def __init__(self, model: RuleSystem) -> None:
        assert PacketWindow.instance is None
        super().__init__()

        self.model: RuleSystem = model
        self.resize(600, 400)

        self.setWindowTitle("Csomagküldés")

        self.setStyleSheet(
            """
            background-color: #1C1C1E;
            color: #BABBBE;
            font-family: Consolas;
            font-size: 16px;
        """
        )
        self.run_button = QPushButton("Futtatás", self)
        self.input_label = QLabel("Bemeneti fájl:", self)
        self.output_label = QLabel("Kimeneti fájl:", self)
        self.input_text = QLineEdit(self)
        self.output_text = QLineEdit(self)
        self.table = QComboBox(self)
        self.chain = QComboBox(self)

        self.main_layout = QGridLayout()

        self.main_layout.addWidget(self.input_label, 0, 0)
        self.main_layout.addWidget(self.input_text, 1, 0, 1, 2)
        self.main_layout.addWidget(self.output_label, 2, 0)
        self.main_layout.addWidget(self.output_text, 3, 0, 1, 2)
        self.main_layout.addWidget(self.table, 4, 0)
        self.main_layout.addWidget(self.chain, 4, 1)
        self.main_layout.addWidget(self.run_button, 5, 1)

        self.setLayout(self.main_layout)

        self.table.addItems(["Válassz"] + list(self.model.tables.keys()))
        self.chain.addItems(["Válassz"])

        @Slot(str)
        def reinit_chain_values(text: str) -> None:
            if text in self.model.tables:
                self.chain.clear()
                self.chain.addItems(
                    ["Válassz"] + list(self.model.get_chain_names(text))
                )
            else:
                self.chain.clear()
                self.chain.addItems(["Válassz"])

        self.table.currentTextChanged.connect(reinit_chain_values)  # type: ignore

        @Slot()
        def run_packet():
            if self.table.currentText() in self.model.tables:
                table = self.table.currentText()
                if self.chain.currentText() in self.model.get_chain_names(table):
                    input_file = self.input_text.text()
                    output_file = self.output_text.text()
                    if (
                        sum(
                            output_file.count(c)
                            for c in ["|", "<", ">", ":", '"', "?", "*"]
                        )
                        == 0
                    ) and os.path.isfile(input_file):
                        self.model.run_chain_on_raw_packets(
                            input_file, output_file, table, self.chain.currentText()
                        )

        self.run_button.clicked.connect(run_packet)  # type: ignore

        PacketWindow.instance = self
        assert log_gui("PacketWindow opened")

    @staticmethod
    def __instance_deleted():
        """
        Set instance to None
        """
        PacketWindow.instance = None

    @override
    def closeEvent(self, event: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
        handling close event
        """
        assert log_gui("PacketWindow closed")
        super().closeEvent(event)
        PacketWindow.__instance_deleted()
        self.deleteLater()

    @staticmethod
    def get_instance(model: Optional[Any] = None) -> PacketWindow:
        """
        Returns the instance of this class

        If no intance is created, creates one
        """
        assert (model is None) or (PacketWindow.instance is None)
        return PacketWindow.instance or PacketWindow(model=model)

    @staticmethod
    def delete_instance() -> None:
        """
        Deletes the only instance if exists
        """
        if PacketWindow.instance is not None:
            PacketWindow.instance.close()

    @Slot()
    def delete_clicked(self) -> None:
        """
        handle delete clicked
        """
        inds: List[int] = self._get_selected_indices()
        if len(inds) == 0:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Message")
            msg_box.setText("No selected items")
            msg_box.exec()
            return
        for ind in inds:
            self.delete_row(ind)


@Slot()
def get_packet_window(model: RuleSystem) -> None:
    """
    Display the packet manager
    """
    model = model if PacketWindow.instance is None else None
    PacketWindow.get_instance(model).show()
    PacketWindow.get_instance().activateWindow()
