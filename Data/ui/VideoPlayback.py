from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QHBoxLayout,
                               QWidget, QSlider)
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, Qt
import os

from .GraphView import GraphView

class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            new_value = int((event.position().x() / self.width()) * self.maximum())
            self.setValue(new_value)
            self.sliderMoved.emit(new_value)
        super().mousePressEvent(event)

class VideoPlayback(QWidget):
    def __init__(self, video_path, data_path, self_main):
        super().__init__()
        self.initUI(video_path, data_path, self_main)

    def initUI(self, video_path, data_path, self_main):

        self.base_path = os.path.dirname(os.path.abspath(__file__))

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setSource(QUrl.fromLocalFile(video_path))

        self.pause_resume_btn = QPushButton()
        self.pause_resume_btn.setIcon(QIcon(os.path.join(self.base_path, "../icons/video_play.png")))
        self.pause_resume_btn.setIconSize(QPixmap(40, 40).size())
        self.pause_resume_btn.setFixedSize(40, 40)
        self.pause_resume_btn.setStyleSheet("border: none;")
        self.pause_resume_btn.clicked.connect(self.toggle_play_pause)

        self.slider = ClickableSlider(Qt.Horizontal)
        self.slider.setMaximum(100)
        self.slider.sliderMoved.connect(self.set_position)

        self.bottom_bar = QWidget()
        self.bottom_bar.setFixedHeight(50)
        self.bottom_bar_layout = QHBoxLayout(self.bottom_bar)
        self.bottom_bar_layout.setContentsMargins(10, 0, 10, 0)
        self.bottom_bar_layout.addWidget(self.pause_resume_btn)
        self.bottom_bar_layout.addWidget(self.slider)

        video_layout = QVBoxLayout()
        video_layout.addWidget(self.video_widget)
        video_layout.addWidget(self.bottom_bar)

        self.main_layout.addLayout(video_layout)

        self.media_player.positionChanged.connect(self.update_slider)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)

        self.cur_pos = "resume"
        self.media_player.pause()

        self.graph_window = GraphView(data_path, self_main)
        self.graph_window.show()

    def toggle_play_pause(self):
        if self.cur_pos == "resume":
            self.media_player.play()
            self.pause_resume_btn.setIcon(QIcon(os.path.join(self.base_path, "../icons/video_pause.png")))
            self.cur_pos = "pause"
        else:
            self.media_player.pause()
            self.pause_resume_btn.setIcon(QIcon(os.path.join(self.base_path, "../icons/video_play.png")))
            self.cur_pos = "resume"

    def set_position(self, position):
        duration = self.media_player.duration()
        if duration > 0:
            new_position = int((position / self.slider.maximum()) * duration)
            self.media_player.setPosition(new_position)

    def update_slider(self, position):
        duration = self.media_player.duration()
        if duration > 0:
            slider_value = int((position / duration) * self.slider.maximum())
            self.slider.setValue(slider_value)

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.reset_playback()

    def reset_playback(self):
        self.media_player.pause()
        self.media_player.setPosition(0)
        self.pause_resume_btn.setIcon(QIcon(os.path.join(self.base_path, "../icons/video_play.png")))
        self.cur_pos = "resume"