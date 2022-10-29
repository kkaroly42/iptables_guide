"""
    Main program
"""
import sys

from PySide6.QtWidgets import QApplication  # pylint: disable=import-error

from gui_project.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
