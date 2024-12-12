from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QHBoxLayout,
                               QWidget, QSlider)
import os

from ..ui.VideoViewer import VideoViewer

class AnalysisView(QWidget):
    def __init__(self, back_callback, set_image_callback, frame_count, self_main):
        super().__init__()
        self.initUI(back_callback, set_image_callback, frame_count, self_main)

    def initUI(self, back_callback, set_image_callback, frame_count, self_main):
        main_layout = QHBoxLayout(self)

        self.base_path = os.path.dirname(os.path.abspath(__file__))

        main_layout.setContentsMargins(0, 0, 0, 0)

        content_layout = QVBoxLayout()
        info_bar = QHBoxLayout()

        back_button = self.createIconButton("icons/back.png", back_callback, 60, 60)
        back_button.setObjectName("back_button")

        website_button = QPushButton("Web")
        website_button.setObjectName("website_button")
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aidetection.great-site.net/")))

        info_bar.addWidget(back_button)
        info_bar.addStretch()
        info_bar.addWidget(website_button)

        self.viewer = VideoViewer()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(0)
        self.slider.setMaximum(frame_count - 2)
        self.slider.setEnabled(False)

        content_layout.addLayout(info_bar)
        content_layout.addWidget(self.viewer)
        content_layout.addWidget(self.slider)

        main_layout.addLayout(content_layout, 4)

    def createIconButton(self, icon_path, callback, width, height, size=32):
        button = QPushButton()
        button.setIcon(QIcon(os.path.join(self.base_path, f"../{icon_path}")))
        button.setIconSize(QPixmap(size, size).size())
        button.setFixedSize(width, height)
        button.setStyleSheet("border: none;")
        button.clicked.connect(callback)
        return button