from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QHBoxLayout,
                               QWidget, QFileDialog)
import os

class VideoSelectorView(QWidget):
    def __init__(self, show_line_selector_callback, show_mode_selector_callback, set_video_data, self_main):
        super().__init__()
        self.initUI(show_line_selector_callback, show_mode_selector_callback, set_video_data, self_main)

    def initUI(self, show_line_selector_callback, show_mode_selector_callback, set_video_data, self_main):
        self_main.start_enabled = False
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        main_layout = QHBoxLayout(self)
        content_layout = QVBoxLayout()

        main_layout.setContentsMargins(0, 0, 0, 0)

        top_bar = QHBoxLayout()
        back_button = self.createIconButton("icons/back.png", show_mode_selector_callback, 60, 60)
        back_button.setObjectName("back_button")

        website_button = QPushButton("Web")
        website_button.setObjectName("website_button")
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aidetection.great-site.net/")))

        top_bar.addWidget(back_button, alignment=Qt.AlignTop | Qt.AlignLeft)
        top_bar.addWidget(website_button, alignment=Qt.AlignTop | Qt.AlignRight)
        content_layout.addLayout(top_bar)

        select_file_button = QPushButton("Select a File to Process")
        select_file_button.setFixedSize(200, 50)
        select_file_button.setObjectName("select_file_button")
        center_layout = QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(select_file_button, alignment=Qt.AlignCenter)
        center_layout.addStretch()

        content_layout.addLayout(center_layout)

        main_layout.addLayout(content_layout, 4)
        select_file_button.clicked.connect(lambda: self.selectFile(show_line_selector_callback, set_video_data))

    def createIconButton(self, icon_path, callback, width, height, size=32):
        button = QPushButton()
        button.setIcon(QIcon(os.path.join(self.base_path, f"../{icon_path}")))
        button.setIconSize(QPixmap(size, size).size())
        button.setFixedSize(width, height)
        button.setStyleSheet("border: none;")
        button.clicked.connect(callback)
        return button

    def selectFile(self, show_line_selector_callback, set_video_data):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_path:
            video_path = file_path
            set_video_data(video_path)
            show_line_selector_callback()