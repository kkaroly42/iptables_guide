"""
    Packet manager window
"""
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
    QCheckBox,
    QDialog,
    QComboBox,
    QLabel,
    QGridLayout,
)

from IPTables_Guide.view.abstract_table_window import AbstractTableWindow
from IPTables_Guide.view.gui_utils import log_gui

from IPTables_Guide.model.packets import PacketType, Packet
from IPTables_Guide.model.rule_system import RuleSystem

'''
class CreatorDialog(QDialog):
    """
    dialog for creating a packet
    """

    def __init__(
        self,
        parent: QWidget,
        packet_type: Optional[PacketType] = None,
        packet: Optional[Packet] = None,  # TODO change if necessary
    ) -> None:
        super().__init__(parent)
        assert packet or packet_type
        if (packet is not None) and (packet_type is not None):
            # TODO check if the packet_type is correct
            pass
        elif packet is not None:
            # TODO set correct packet_type
            pass

        self.packet = packet
        self.setWindowTitle("Csomagküldés")

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.preferences = QPlainTextEdit(self)
        self.main_layout.addWidget(self.preferences)

        self.return_layout = QHBoxLayout()
        self.main_layout.addLayout(self.return_layout)

        self.accept_button = QPushButton("Apply", self)
        self.reject_button = QPushButton("Cancel", self)

        self.return_layout.addWidget(self.accept_button)
        self.return_layout.addWidget(self.reject_button)

        self.accept_button.clicked.connect(self.added)  # type: ignore
        self.reject_button.clicked.connect(self.close)  # type: ignore

        if packet_type is PacketType.TCP:
            self.setWindowTitle("TCP packet config")
            self.preferences.setPlainText(
                "from_adress=localhost\n"
                "from_port=10000\n"
                "to_adress=localhost\n"
                "to_port=10001\n"
                "packet_size=10\n"
            )
        elif packet_type is PacketType.UDP:
            self.setWindowTitle("UDP packet config")
            self.preferences.setPlainText(
                "from_adress=localhost\n"
                "from_port=10000\n"
                "to_adress=localhost\n"
                "to_port=10001\n"
                "packet_size=10\n"
            )
        else:
            assert False

    @override
    def closeEvent(self, arg__1: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
        handling close event
        """
        msg_box = QMessageBox()
        msg_box.setStandardButtons(
            QMessageBox.Ok | QMessageBox.Cancel)  # type: ignore
        msg_box.setText("Your changes wont be saved.")
        ret: int = msg_box.exec()
        if ret == QMessageBox.Cancel:  # type: ignore
            arg__1.ignore()
            return
        assert log_gui("PacketWindow closed")
        # TODO
        super().closeEvent(arg__1)

    @Slot()
    def added(self):
        """
        handle if the user choiced add

        check if the given text has a valid format
        """
        line: str = self.preferences.toPlainText()
        line = line.replace("\r", "").replace(" ", "").replace("\t", "")
        lines: List[str] = line.split("\n")
        lines = [l for l in lines if l != ""]
        if any(l.count("=") != 1 for l in lines):
            msg_box = QMessageBox()
            msg_box.setText("A line must contain exactly 1 '='")
            msg_box.exec()
            return
        if self.packet is not None:
            # TODO set preferences
            pass
        self.accept()
'''


class PacketWindow(QWidget):
    """"""

    _instance: Optional["PacketWindow"] = None

    def __init__(self, model: RuleSystem) -> None:
        assert PacketWindow._instance is None
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

        self.table.addItems(["Válassz"] + list(self.model._tables.keys()))
        self.chain.addItems(["Válassz"])

        @Slot(str)
        def reinit_chain_values(text: str) -> None:
            if text in self.model._tables:
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
            if self.table.currentText() in self.model._tables:
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

        PacketWindow._instance = self
        assert log_gui("PacketWindow opened")

    @staticmethod
    def __instance_deleted():
        """
        Set instance to None
        """
        PacketWindow._instance = None

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
    def get_instance(model: Optional[Any] = None) -> "PacketWindow":
        """
        Returns the instance of this class

        If no intance is created, creates one
        """
        assert (model is None) or (PacketWindow._instance is None)
        return PacketWindow._instance or PacketWindow(model=model)

    @staticmethod
    def delete_instance() -> None:
        """
        Deletes the only instance if exists
        """
        if PacketWindow._instance is not None:
            PacketWindow._instance.close()

    @Slot()
    def delete_clicked(self) -> None:
        """
        handle delete clicked
        """
        inds: List[int] = self._get_selected_indices()
        if len(inds) == 0:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Törlés hiba")
            msg_box.setText("Nincsenek kiválasztott törlendő elemek.")
            msg_box.exec()
            return
        for ind in inds:
            self.delete_row(ind)


@Slot()
def get_packet_window(model) -> None:
    """
    Display the packet manager
    """
    model = model if PacketWindow._instance is None else None
    PacketWindow.get_instance(model).show()
    PacketWindow.get_instance().activateWindow()
