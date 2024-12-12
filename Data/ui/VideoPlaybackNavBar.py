from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QWidget, QSpacerItem,
                               QSizePolicy)
import os

class VideoPlaybackNavBar(QWidget):
    def __init__(self, self_main, graphView):
        super().__init__()
        self.initUI(self_main, graphView)

    def initUI(self, self_main, graphView):
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        nav_layout = QVBoxLayout(self)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setFixedWidth(60)

        self.back_button = self.createIconButton("icons/back.png", 40, 40)
        self.back_button.setObjectName("back_button")
        self.back_button.clicked.connect(self_main.showHistoryView)
        nav_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        self.quit_button = self.createIconButton("icons/exit.png", 40, 40)
        self.quit_button.clicked.connect(lambda: self_main.historyCloseCallback(graphView))

        nav_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        nav_layout.addWidget(self.quit_button, alignment=Qt.AlignCenter)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#313131"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def createIconButton(self, icon_path, width, height, size=32):
        button = QPushButton()
        button.setIcon(QIcon(os.path.join(self.base_path, f"../{icon_path}")))
        button.setIconSize(QPixmap(size, size).size())
        button.setFixedSize(width, height)
        button.setStyleSheet("border: none;")
        return button