"""
    Packet manager window
"""
from __future__ import annotations

from typing import Optional, Any, List, Dict
from overrides import override  # type: ignore # pylint: disable=import-error


from PySide6.QtCore import Slot  # type: ignore # pylint: disable=import-error
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtGui import QCloseEvent  # type: ignore # pylint: disable=import-error
from PySide6.QtWidgets import (  # type: ignore # pylint: disable=import-error
    QWidget,
    QMessageBox,
    QPushButton,
    QCheckBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QMainWindow,
)

from pathlib import Path

from IPTables_Guide.view.abstract_table_window import AbstractTableWindow
from IPTables_Guide.view.gui_utils import log_gui, Button

from IPTables_Guide.model.packets import PacketType, Packet, PacketManager

import IPTables_Guide.model as model


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
            assert packet.get_type() == packet_type
        elif packet is not None:
            packet_type = packet.get_type()

        self.packet = packet
        self.packet_type = packet_type
        self.modified = False
        self.setWindowTitle("Csomagkészítés")

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.preferences = QTreeWidget()
        self.preferences.setColumnCount(2)
        self.preferences.setHeaderLabels(["Key", "Value"])
        self.main_layout.addWidget(self.preferences)

        self.return_layout = QHBoxLayout()
        self.main_layout.addLayout(self.return_layout)

        self.accept_button = QPushButton("Apply", self)
        self.reject_button = QPushButton("Cancel", self)

        self.return_layout.addWidget(self.accept_button)
        self.return_layout.addWidget(self.reject_button)

        self.accept_button.clicked.connect(self.added)  # type: ignore
        self.reject_button.clicked.connect(self.close)  # type: ignore

        self.setWindowTitle(f"{packet_type} packet config")
        self.preferences.itemChanged.connect(self.handle_item_change)
        self.preferences.setMouseTracking(True)
        if self.packet is None:
            assert self.packet_type
            self.config = model.DUMMY_PACKETS[self.packet_type].get_fields()
        else:
            self.config = self.packet.get_fields()
        items: List[QTreeWidgetItem] = []
        for protocol, value in self.config.items():
            item = QTreeWidgetItem([protocol])
            for flag, flag_value in value.items():
                item2 = QTreeWidgetItem([flag, str(flag_value.value)])
                item2.setFlags(item2.flags() | Qt.ItemIsEditable)
                item2.setToolTip(0, flag_value.explanation)
                item.addChild(item2)
            items.append(item)

        self.preferences.insertTopLevelItems(0, items)

    @override
    def closeEvent(self, arg__1: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
        handling close event
        """
        msg_box = QMessageBox()
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # type: ignore
        msg_box.setText("A változtatások nem lesznek mentve.")
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
        ethernet_args = {k: v.value for k, v in self.config["Ethernet"].items()}
        internet_layer_fields = {k: v.value for k, v in self.config["IP"].items()}
        transmission_layer_fields = {
            k: v.value for k, v in self.config[str(self.packet_type)].items()
        }

        if self.modified or self.packet is None:
            self.packet = PacketManager.create_packet(
                self.packet_type,
                ethernet_args,
                internet_layer_fields,
                transmission_layer_fields,
            )
        self.accept()

    @Slot()
    def handle_item_change(self, item: QTreeWidgetItem):
        protocol = item.parent().text(0)
        tmp = self.config[protocol]
        t = tmp[item.text(0)].type_
        tmp[item.text(0)].value = t(item.text(1))
        if not self.modified:
            self.modified = True


# TODO handle delete on gui
class PacketCreationWindow(AbstractTableWindow):
    """
    Window managing packets
    """

    def __init__(self, parent: Optional[QMainWindow], **kwargs) -> None:
        """ """
        super().__init__(
            "Packets",
            [
                ("select", QCheckBox),
                ("name", QPushButton),
            ],
            parent,
        )
        kwargs = kwargs.get("kwargs", kwargs)

        assert "packet_manager" in kwargs

        self._packet_manager: PacketManager = kwargs["packet_manager"]

        self._parent = parent
        self.resize(600, 400)

        self.buttons: Dict[str, Button] = {
            "tcp": Button(
                btn=QPushButton("TCP", self.centralWidget()),
                call=lambda: self.create_packet(PacketType.TCP),
            ),
            "udp": Button(
                btn=QPushButton("UDP", self.centralWidget()),
                call=lambda: self.create_packet(PacketType.UDP),
            ),
            "delete": Button(
                btn=QPushButton("törlés", self.centralWidget()),
                call=self.delete_clicked,
            ),
            "clear": Button(
                btn=QPushButton("összes törlése", self.centralWidget()), call=self.clear
            ),
        }
        self.menu_line_buttons: Dict[str, Button] = {
            "load": Button(
                btn=QPushButton("betöltés", self.centralWidget()), call=self.load_pcap
            ),
            "write": Button(
                btn=QPushButton("mentés", self.centralWidget()), call=self.write_pcap
            ),
        }
        self.setWindowTitle("Csomagkészítés")

        self.setStyleSheet(
            """
            background-color: #1C1C1E;
            color: #BABBBE;
            font-family: Consolas;
            font-size: 16px;
            """
        )
        for _, v in self.buttons.items():
            btn = v.btn
            btn.setStyleSheet(
                """
                 QPushButton {
                    background-color: #2F2F32;
                    color: #BABBBE;
                    font-family: Consolas;
                    font-size: 16px;
                    padding: 6px 3px 6px 3px;
                    border: 1px solid #505054;
                    margin: 0px;
                }
                QPushButton:pressed{
                    background-color: #28282B;
                    color: #BABBBE;
                    border: 1px solid #28282B;
                }
                QPushButton:hover:!pressed {
                    background-color: #505054;
                    color: white;
                }
                """
            )
            self.menu_line.layout().addWidget(btn)
            btn.clicked.connect(v.call)  # type: ignore

        self.menu_line.layout().insertStretch(-1)  # type: ignore
        for _, v in self.menu_line_buttons.items():
            btn = v.btn
            btn.setStyleSheet(
                """
                 QPushButton {
                    background-color: #2F2F32;
                    color: #BABBBE;
                    font-family: Consolas;
                    font-size: 16px;
                    padding: 6px 3px 6px 3px;
                    border: 1px solid #505054;
                    margin: 0px;
                }
                QPushButton:pressed{
                    background-color: #28282B;
                    color: #BABBBE;
                    border: 1px solid #28282B;
                }
                QPushButton:hover:!pressed {
                    background-color: #505054;
                    color: white;
                }
                """
            )
            self.menu_line.layout().addWidget(btn)
            btn.clicked.connect(v.call)

        self.menu_line.setStyleSheet(
            """
            background-color: #2F2F32;
            color: #BABABE;
            """
        )

        self.update_table()
        assert log_gui("PacketWindow opened")

    @Slot()
    def create_packet(self, packet_type: PacketType):
        """
        open a dialog with TCP template
        """
        dialog = CreatorDialog(self, packet_type=packet_type)
        dialog.accepted.connect(
            lambda: self.add_packet(dialog.packet) if dialog.packet else None
        )
        dialog.exec()

    @Slot()
    def view_packet(self, id_: int):
        dialog = CreatorDialog(self, packet=self._packet_manager.get(id_))
        dialog.accepted.connect(
            lambda: self.maybe_modify_packet(id_, dialog.packet, dialog.modified)
            if dialog.packet
            else None
        )
        dialog.exec()

    def add_packet(self, packet: Packet) -> None:
        """
        add packet to table
        """
        self._packet_manager.add_packet(packet)
        self.append_row()

    @Slot()
    def load_pcap(self):
        file = Path(QFileDialog.getOpenFileName(self)[0])
        self.clear()
        self._packet_manager.read_pcap(file)
        self.update_table()

    def update_table(self):
        for _ in self._packet_manager:
            self.append_row()

    def write_pcap(self):
        file = Path(QFileDialog.getSaveFileName(self)[0])
        self._packet_manager.write(file, False)

    def maybe_modify_packet(
        self, packet_id: int, packet: Packet, modified: bool
    ) -> None:
        if not modified:
            return None
        self._packet_manager.set(packet_id, packet)

    def clear(self):
        self._packet_manager.clear()
        self.table.clear_table()

    @override
    def _set_row(self, ind: int) -> None:
        self.table[ind, "name"].clicked.connect(lambda: self.view_packet(ind))
        packet_type = self._packet_manager.get(ind).get_type()
        self.table[ind, "name"].setText(
            PacketCreationWindow._build_packet_text(ind, packet_type)
        )

    @Slot()
    def delete_clicked(self) -> None:
        """
        handle delete clicked
        """
        inds: List[int] = self._get_selected_indices()
        if len(inds) == 0:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Törlés hiba")
            msg_box.setText("Nincsenek kiválasztott törlendő elemek.")
            msg_box.exec()
            return
        for ind in reversed(inds):
            self._packet_manager.del_packet(ind)
            self.delete_row(ind)

        for i in range(len(self._packet_manager)):
            self.table[i, "name"].setText(
                PacketCreationWindow._build_packet_text(
                    i, self._packet_manager.get(i).get_type()
                )
            )

    @staticmethod
    def _build_packet_text(i: int, type_: Optional[PacketType]) -> str:
        if type_:
            return f"packet id {i} ({type_} packet)"
        else:
            return f"packet id {i}"
