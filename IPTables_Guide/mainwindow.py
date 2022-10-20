# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QLineEdit

from IPTables_Guide.custom_table_widget import CustomTableWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.tableWidget = CustomTableWidget(
            [("button", QPushButton), ("textbox", QLineEdit)], self)

        self.mainLayout = QHBoxLayout()
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.tableWidget)

        self.tableWidget.add_row()

        self.tableWidget[0]["button"].setText('alma')   # type: ignore
        self.tableWidget.insert_row(0)
        self.tableWidget.add_row()

        del self.tableWidget[[1]]

        self.tableWidget.apply_method_to_row(
            [0, 1], lambda w: w.setMaximumHeight(1000))
        for i, w in enumerate(self.tableWidget.get_column("button")):
            w.setText(str(i))  # type: ignore
        self.tableWidget.apply_method_to_column("textbox", lambda w: w.setReadOnly(True))  # type: ignore

        self.tableWidget.add_row()

        self.tableWidget.apply_method_to_row(2, lambda w: w.setText("Hello"))  # type: ignore


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
