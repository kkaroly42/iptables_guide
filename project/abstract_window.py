"""
    abstract window providing the same interface
"""

from typing import Optional, List, Tuple
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
)

from custom_table_widget import CustomTableWidget


class AbstractWindow(QMainWindow):
    """
        Window representing a table
    """

    def __init__(
        self,
        table_name: str,
        row_types: List[Tuple[str, type]],
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        """
        super().__init__(parent)
        self.setCentralWidget(QWidget(self))
        self.main_layout = QHBoxLayout()
        self.centralWidget().setLayout(self.main_layout)

        self.menu_line = QWidget(self.centralWidget())
        self.menu_line.setMaximumWidth(200)
        self.table = CustomTableWidget(row_types, self.centralWidget(),)

        self.main_layout.addWidget(self.menu_line)
        self.table_layout = QVBoxLayout()
        self.table_layout.addWidget(QLabel(table_name, self.centralWidget()))
        self.table_layout.addWidget(self.table)
        self.table_layout.insertStretch(-1)
        self.main_layout.addLayout(self.table_layout)

        self.menu_line.setLayout(QVBoxLayout())

    def _get_selected_indices(self) -> List[int]:
        return [
            i
            for i, w in enumerate(self.table.get_column("select"))
            if w.isChecked()  # type: ignore
        ]
