"""
    test file
"""
# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
)
from PySide6.QtWebEngineWidgets import QWebEngineView  # pylint: disable=import-error
from PySide6.QtCore import QUrl  # pylint: disable=import-error

from custom_table_widget import CustomTableWidget


class MainWindow(QMainWindow):
    """
        test class
    """

    def __init__(self):
        super().__init__()

        self.table_widget = CustomTableWidget(
            [("button", QPushButton), ("textbox", QLineEdit)], self
        )

        self.main_layout = QHBoxLayout()
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(self.main_layout)

        self.main_layout.addWidget(self.table_widget)

        self.table_widget.add_row()

        self.table_widget[0]["button"].setText("alma")  # type: ignore
        self.table_widget.insert_row(0)
        self.table_widget.add_row()

        del self.table_widget[[1]]

        self.table_widget.apply_method_to_row(
            [0, 1], lambda w: w.setMaximumHeight(1000)
        )
        for i, widget in enumerate(self.table_widget.get_column("button")):
            widget.setText(str(i))  # type: ignore
        self.table_widget.apply_method_to_column(
            "textbox", lambda w: w.setReadOnly(True)  # type: ignore
        )

        self.table_widget.add_row()

        self.table_widget.apply_method_to_row(
            2, lambda w: w.setText("Hello")  # type: ignore
        )
        self.table_widget[2, "textbox"].setToolTip(  # type: ignore
            "It's a tootip!"
        )

        # help menu
        dialog = QMainWindow(self)
        dialog.show()
        dialog.resize(600, 800)
        view = QWebEngineView(dialog)
        dialog.setCentralWidget(view)
        # view.setUrl(QUrl("https://www.google.com"))
        view.setUrl(QUrl("./.index.html"))


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
