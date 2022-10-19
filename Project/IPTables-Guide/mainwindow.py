# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QLineEdit

from custom_table_widget import CustomTableWidget


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

        self.tableWidget[0]["button"].setText('alma')
        self.tableWidget.insert_row(0)
        self.tableWidget.add_row()

        self.tableWidget.delete_row(1)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
