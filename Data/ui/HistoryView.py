from datetime import datetime
import os
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QHBoxLayout,
                               QWidget, QLabel, QScrollArea, QFrame)

from ..core.Saving import get_history

class HistoryView(QWidget):
    def __init__(self, show_mode_selector_callback, self_main):
        super().__init__()
        self.initUI(show_mode_selector_callback, self_main)

    def initUI(self, show_mode_selector_callback, self_main):
        main_layout = QHBoxLayout(self)
        top_bar = QHBoxLayout()
        content_layout = QVBoxLayout()

        self.base_path = os.path.dirname(os.path.abspath(__file__))

        main_layout.setContentsMargins(0, 0, 0, 0)

        back_button = self.createIconButton("icons/back.png", show_mode_selector_callback, 60, 60)
        back_button.setObjectName("back_button")

        website_button = QPushButton("Web")
        website_button.setObjectName("website_button")
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aidetection.great-site.net/")))

        top_bar.addWidget(back_button, alignment=Qt.AlignTop | Qt.AlignLeft)
        top_bar.addStretch()
        top_bar.addWidget(website_button, alignment=Qt.AlignTop | Qt.AlignRight)

        content_layout.addLayout(top_bar)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        video_list_widget = QWidget()
        video_list_layout = QVBoxLayout(video_list_widget)
        video_list_layout.setAlignment(Qt.AlignCenter)

        history_data = get_history()

        for i in history_data.keys():
            item_button = self.createItemButton(history_data[i]["krizovatka"], str(datetime.fromisoformat(history_data[i]["end_time"]) - datetime.fromisoformat(history_data[i]["start_time"])), self_main, i, history_data[i]["data_path"])
            video_list_layout.addWidget(item_button)

        video_list_layout.addStretch()

        video_list_widget.setLayout(video_list_layout)
        scroll_area.setWidget(video_list_widget)

        content_layout.addWidget(scroll_area)
        main_layout.addLayout(content_layout, 4)

    def createIconButton(self, icon_path, callback, width, height, size=32):
        button = QPushButton()
        button.setIcon(QIcon(os.path.join(self.base_path, f"../{icon_path}")))
        button.setIconSize(QPixmap(size, size).size())
        button.setFixedSize(width, height)
        button.setStyleSheet("border: none;")
        button.clicked.connect(callback)
        return button

    def createItemButton(self, video_name, video_time, self_main, ouput_path, data_path):
        button = QPushButton()
        button.clicked.connect(lambda: self_main.showVideoPlaybackView(ouput_path, data_path))
        button.setObjectName("history_item")
        button.setFixedSize(600, 100)
        button.setStyleSheet("text-align: left; border: none;")

        item_layout = QHBoxLayout(button)
        item_layout.setContentsMargins(10, 0, 0, 0)

        thumbnail_label = QLabel()
        thumbnail_pixmap = QPixmap(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../icons/placeholder.jpg")
        ).scaled(125, 200, Qt.AspectRatioMode.KeepAspectRatio)
        thumbnail_label.setPixmap(thumbnail_pixmap)
        thumbnail_label.setFixedSize(125, 75)

        name_label = QLabel(video_name)
        name_label.setObjectName("history_name")
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        time_label = QLabel(video_time)
        time_label.setObjectName("history_time")
        time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        item_layout.addWidget(thumbnail_label)
        item_layout.addWidget(name_label, stretch=1)
        item_layout.addWidget(time_label)

        button.setLayout(item_layout)
        return button
