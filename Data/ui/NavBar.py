from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QWidget, QSpacerItem,
                               QSizePolicy)
import os

class NavBar(QWidget):
    def __init__(self, showAnalysis_callback, stopAnalysis_callback, close_callback):
        super().__init__()
        self.initUI(showAnalysis_callback, stopAnalysis_callback, close_callback)

    def initUI(self, showAnalysis_callback, stopAnalysis_callback, close_callback):
        nav_layout = QVBoxLayout(self)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setFixedWidth(60)

        self.base_path = os.path.dirname(os.path.abspath(__file__))

        self.quit_button = self.createIconButton("icons/exit.png", 40, 40)
        self.quit_button.clicked.connect(close_callback)

        self.start_button = self.createIconButton("icons/dis_play.png", 40, 40)

        self.start_button.clicked.connect(showAnalysis_callback)

        self.stop_button = self.createIconButton("icons/dis_stop.png", 40, 40)
        self.stop_button.clicked.connect(stopAnalysis_callback)
        nav_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        nav_layout.addWidget(self.stop_button, alignment=Qt.AlignCenter)
        nav_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        nav_layout.addWidget(self.quit_button, alignment=Qt.AlignCenter)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#313131"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
    def toogle_startButton(self, on):
        if on:
            self.start_button.setIcon(QIcon(os.path.join(self.base_path, "../icons/play.png")))
        else:
            self.start_button.setIcon(QIcon(os.path.join(self.base_path, "../icons/dis_play.png")))
        self.start_button.setEnabled(on)

    def toogle_stopButton(self, on):
        if on:
            self.stop_button.setIcon(QIcon(os.path.join(self.base_path, "../icons/stop.png")))
        else:
            self.stop_button.setIcon(QIcon(os.path.join(self.base_path, "../icons/dis_stop.png")))
        self.stop_button.setEnabled(on)

    def createIconButton(self, icon_path, width, height, size=32):
        button = QPushButton()
        button.setIcon(QIcon(os.path.join(self.base_path, f"../{icon_path}")))
        button.setIconSize(QPixmap(size, size).size())
        button.setFixedSize(width, height)
        button.setStyleSheet("border: none;")
        return button