"""
    Main program
"""
import sys

from PySide6.QtWidgets import QApplication  # pylint: disable=import-error

from IPTables_Guide.view.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(
        """
        QScrollArea {
            border: 0px;
        }
        QScrollBar:vertical {
            border: 0px solid grey;
            background: #1C1C1E;
            width: 10px;
            margin: 0px 0 0px 0;
        }
        QScrollBar::handle:vertical {
            background: #2F2F32;
            border-radius: 5px;
            min-height: 20px;
        }
        QScrollBar::add-line:vertical {
            border: 0px solid grey;
            height: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:vertical {
            border: 0px;
            height: 0px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            border: 0px;
            width: 0px;
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        QRadioButton::indicator {
            width: 12px;
            height: 12px;
        }
        QRadioButton::indicator::unchecked {
            background-color: #1C1C1E;
        }

        QRadioButton::indicator:unchecked:hover {
            background-color: #BABABE;
        }

        QRadioButton::indicator:unchecked:pressed {
            background-color: #707070;
        }

        QRadioButton::indicator::checked {
            background-color: #A2D5AC;
        }

        QCheckBox::indicator {
            width: 14px;
            height: 14px;
        }
        QCheckBox::indicator:unchecked {
            background-color: #2F2F32;
        }
        QCheckBox::indicator:unchecked:hover {
            background-color: #BABABE;
        }
        QCheckBox::indicator:unchecked:pressed {
            background-color: #707070;
        }
        QCheckBox::indicator:checked {
            background-color: #3AAFC3;
        }
        QCheckBox::indicator:checked:hover {
            background-color: #76C7D6;
        }
        QCheckBox::indicator:checked:pressed {
            background-color: #707070;
        }
    """
    )
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
