"""
    HelpWindow class
"""
from typing import Optional  # type: ignore
from overrides import override  # pylint: disable=import-error
from PySide6.QtWebEngineWidgets import QWebEngineView  # pylint: disable=import-error
from PySide6.QtGui import QCloseEvent  # pylint: disable=import-error
from PySide6.QtCore import (  # pylint: disable=import-error
    Signal,
    QUrl,
)
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QWidget,
    QMainWindow,
)


class HelpWindow(QMainWindow):
    """
        Window displaying the help manual
    """

    closed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        """
        super().__init__(parent)
        view = QWebEngineView(self)
        self.setCentralWidget(view)
        view.setUrl(QUrl("./.index.html"))
        self.resize(600, 800)

    @override
    def closeEvent(self, event: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
            handling close event
        """
        super().closeEvent(event)
        self.closed.emit()
