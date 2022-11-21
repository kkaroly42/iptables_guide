"""
    Packet manager window
"""

from typing import Optional, Any, List
from overrides import override  # pylint: disable=import-error

from IPTables_Guide.model.packets import PacketType, Packet

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
    QPlainTextEdit,
    QVBoxLayout,
    QHBoxLayout,
)

from IPTables_Guide.view.abstract_table_window import AbstractTableWindow
from IPTables_Guide.view.gui_utils import log_gui


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
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # type: ignore
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


class PacketWindow(AbstractTableWindow):
    """
    Window managing packets
    """

    _instance: Optional["PacketWindow"] = None

    def __init__(self, **kwargs) -> None:
        """ """
        assert PacketWindow._instance is None
        super().__init__(
            "Packets",
            [
                ("select", QCheckBox),
                ("name", QLineEdit),
                ("open", QPushButton),
            ],
        )
        self.packet_manager = (
            kwargs["packet_manager"] if "packet_manager" in kwargs else None
        )
        self.resize(600, 400)

        self.buttons = {}
        self.setWindowTitle("Csomagküldés")

        self.setStyleSheet("""
            background-color: #1C1C1E;
            color: #BABBBE;
            font-family: Consolas;
            font-size: 16px;
        """)
        
        self.buttons["tcp"] = QPushButton("TCP template", self.centralWidget())
        self.buttons["udp"] = QPushButton("UDP template", self.centralWidget())
        self.buttons["delete"] = QPushButton("Delete", self.centralWidget())

        for key in ["tcp", "udp", "delete"]:
            self.menu_line.layout().addWidget(self.buttons[key])

        self.menu_line.layout().insertStretch(-1)  # type: ignore

        self.menu_line.setStyleSheet("""
            background-color: #2F2F32;
            color: #BABABE;
        """)


        self.buttons["tcp"].clicked.connect(  # type: ignore
            lambda: self.create_packet(PacketType.TCP)
        )
        self.buttons["udp"].clicked.connect(  # type: ignore
            lambda: self.create_packet(PacketType.UDP)
        )
        self.buttons["delete"].clicked.connect(self.delete_row)  # type: ignore

        PacketWindow._instance = self
        assert log_gui("PacketWindow opened")

    @Slot()
    def create_packet(self, packet_type: PacketType):
        """
        open a dialog with TCP template
        """
        dialog = CreatorDialog(self, packet_type=packet_type)
        dialog.accepted.connect(  # type: ignore
            lambda: self.add_packet(packet_type, dialog.preferences.toPlainText())
        )
        dialog.exec()

    @Slot()
    def modify_packet(self, packet: Packet):  # TODO modify if necessary
        """
        open a dialog with TCP template
        """
        dialog = CreatorDialog(self, packet=packet)
        # TODO handle packet modified
        dialog.accepted.connect()  # type: ignore
        dialog.exec()

    def add_packet(self, packet_type: PacketType, preferences: str) -> None:
        """ """
        # TODO API calls
        self.append_row()

    @override
    def _set_row(self, ind: int) -> None:
        packet = None
        self.table[ind, "open"].clicked.connect(  # type: ignore
            # TODO handle packet
            lambda: self.modify_packet(packet)
        )
        self.table[ind, "open"].setText("Modify")  # type: ignore

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
    def get_instance(packet_manager: Optional[Any] = None) -> "PacketWindow":
        """
        Returns the instance of this class

        If no intance is created, creates one
        """
        assert (packet_manager is None) or (PacketWindow._instance is None)
        return PacketWindow._instance or PacketWindow(packet_manager=packet_manager)

    @staticmethod
    def delete_instance() -> None:
        """
        Deletes the only instance if exists
        """
        if PacketWindow._instance is not None:
            PacketWindow._instance.close()


@Slot()
def get_packet_window(packet_manager) -> None:
    """
    Display the packet manager
    """
    packet_manager = packet_manager if PacketWindow._instance is None else None
    PacketWindow.get_instance(packet_manager).show()
    PacketWindow.get_instance().activateWindow()
