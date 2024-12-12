from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QHBoxLayout,
                               QWidget)


class ModeSelectorView(QWidget):
    def __init__(self, show_video_selector_callback, show_history_callback,self_main):
        super().__init__()
        self.initUI(show_video_selector_callback, show_history_callback, self_main)

    def initUI(self, show_video_selector_callback, show_history_callback, self_main):
        main_layout = QHBoxLayout(self)
        top_bar = QHBoxLayout()
        content_layout = QVBoxLayout()

        main_layout.setContentsMargins(0, 0, 0, 0)

        website_button = QPushButton("Web")
        website_button.setObjectName("website_button")
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aidetection.great-site.net/")))

        history_button = QPushButton("History")
        history_button.setObjectName("history_button")
        history_button.clicked.connect(show_history_callback)

        process_live_button = QPushButton("Process Live Footage")
        process_live_button.clicked.connect(lambda: show_video_selector_callback(True))

        process_video_button = QPushButton("Process a Video File")
        process_video_button.clicked.connect(lambda: show_video_selector_callback(False))

        process_live_button.setObjectName("process_live_button")
        process_video_button.setObjectName("process_video_button")

        top_bar.addWidget(history_button, alignment=Qt.AlignTop | Qt.AlignLeft)
        top_bar.addStretch()
        top_bar.addWidget(website_button, alignment=Qt.AlignTop | Qt.AlignRight)

        content_layout.addLayout(top_bar)
        content_layout.addStretch()
        content_layout.addWidget(process_live_button, alignment=Qt.AlignCenter)
        content_layout.addWidget(process_video_button, alignment=Qt.AlignCenter)
        content_layout.addStretch()

        main_layout.addLayout(content_layout, 4)