from PySide6.QtCore import Qt, QUrl, QDateTime
from PySide6.QtGui import QCursor, QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QHBoxLayout,
                               QWidget, QSlider, QLabel, QSpinBox, QComboBox, QDialog)
import os
from datetime import datetime

from ..core.Connection import check_internet_conn
from ..ui.VideoViewer import VideoViewer
from ..ui.Calendar import Calendar
from ..ui.IntersectionSelector import IntersectionSelector
from ..ui.IntersectionSavePopup import IntersectionSavePopup
from Data.core.Saving import save_lines
class LineSelectionView(QWidget):
    def __init__(self, back_callback, frequency_input_callback, set_image_callback, frame_count, fps, local_analysis, live_analysis,self_main):
        super().__init__()
        self.initUI(back_callback, frequency_input_callback, set_image_callback, frame_count, fps, local_analysis, live_analysis, self_main)

    def initUI(self, back_callback, frequency_input_callback, set_image_callback, frame_count, fps, local_analysis, live_analysis, self_main):
        main_layout = QHBoxLayout(self)

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        self_main.start_enabled = True
        main_layout.setContentsMargins(0, 0, 0, 0)

        settings_bar = QHBoxLayout()
        bottom_bar = QHBoxLayout()

        label = QLabel("Data Upload Frequency")
        label.setStyleSheet("font-size: 14px; font-weight: bold;")

        back_button = self.createIconButton("icons/back.png", back_callback, 60, 60)
        back_button.setObjectName("back_button")

        frequency_input = QSpinBox()
        frequency_input.setAlignment(Qt.AlignCenter)
        frequency_input.setMinimum(0)
        frequency_input.setMaximum(99)
        frequency_input.setValue(2)
        frequency_input.setSuffix(" s")
        frequency_input.valueChanged.connect(frequency_input_callback)
        frequency_input.setObjectName("freq_inp")

        model_selector = QComboBox()
        model_selector.addItems(["Quick Analysis", "Accurate Analysis"])
        model_selector.setObjectName("modelSelector")
        model_selector.currentIndexChanged.connect(lambda: self.changeModel(model_selector, self_main))

        if not live_analysis:
            start_label = QLabel("Start")
            start_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")

            self.start_input = Calendar()
            self.start_input.setAlignment(Qt.AlignCenter)
            self.start_input.setDateTime(QDateTime.fromString("2023-01-01T00:00:00", Qt.ISODate))
            self.start_input.setCalendarPopup(True)
            self.start_input.setObjectName("start_inp")

            self_main.start_time = self.convertDateTime(self.start_input.dateTime())

            end_label = QLabel("End")
            end_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")

            self.end_input = Calendar()
            self.end_input.setAlignment(Qt.AlignCenter)
            self.end_input.setMinimumDateTime(self.start_input.dateTime())
            self.end_input.setDateTime(QDateTime.currentDateTime())
            self.end_input.setCalendarPopup(True)
            self.end_input.setObjectName("end_inp")

            self_main.end_time = self.convertDateTime(self.end_input.dateTime())

            self.start_input.dateTimeChanged.connect(lambda: self.videoStartTime(self_main))
            self.end_input.dateTimeChanged.connect(lambda: self.videoEndTime(self_main))
            self.slider = QSlider(Qt.Horizontal)
            self.slider.setMaximum(frame_count - 1)
            self.slider.valueChanged.connect(lambda: set_image_callback())
        else:
            self_main.start_time = datetime.now()

        website_button = QPushButton("Web")
        website_button.setObjectName("website_button")
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aidetection.great-site.net/")))

        self.viewer = VideoViewer()
        self.viewer.setCursor(QCursor(Qt.CrossCursor))



        new_intersection = QPushButton("Save Lines")
        new_intersection.clicked.connect(lambda: self.showIntersectionSavePopup(self_main))
        new_intersection.setObjectName("save_intersection_button")

        choose_intersection = QPushButton("Load Lines")
        choose_intersection.clicked.connect(lambda: self.showIntersectionSelector(self_main))
        choose_intersection.setObjectName("choose_intersection_button")

        reset_button = self.createIconButton("icons/reset.png", lambda: self.resetIntersection(), 60, 60)

        settings_bar.addWidget(back_button)
        settings_bar.addWidget(label)
        settings_bar.addWidget(frequency_input)
        settings_bar.addWidget(model_selector)
        settings_bar.addStretch()
        if not live_analysis:
            settings_bar.addWidget(start_label)
            settings_bar.addWidget(self.start_input)
            settings_bar.addWidget(end_label)
            settings_bar.addWidget(self.end_input)
        settings_bar.addStretch()
        settings_bar.addWidget(website_button)

        bottom_bar.addWidget(new_intersection)
        bottom_bar.addWidget(choose_intersection)
        bottom_bar.addWidget(reset_button)
        bottom_bar.addStretch()

        content_layout = QVBoxLayout()
        content_layout.addLayout(settings_bar)
        content_layout.addWidget(self.viewer)
        if not live_analysis:
            content_layout.addWidget(self.slider)
        content_layout.addLayout(bottom_bar)

        main_layout.addLayout(content_layout, 4)



        self_main.local_analysis = check_internet_conn(frequency_input)

        if self_main.local_analysis:
            label.setStyleSheet("color: #373737; font-size: 14px; font-weight: bold;")
        else:
            label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")

    def changeModel(self, modelSelector, self_main):
        if modelSelector.currentText() == "Quick Analysis":
            self_main.fast_model = True
        else:
            self_main.fast_model = False

    def convertDateTime(self, qdatetime):
        python_datetime = datetime(
            year=qdatetime.date().year(),
            month=qdatetime.date().month(),
            day=qdatetime.date().day(),
            hour=qdatetime.time().hour(),
            minute=qdatetime.time().minute(),
            second=qdatetime.time().second()
        )
        return python_datetime

    def videoStartTime(self, self_main):
        self.end_input.setMinimumDateTime(self.start_input.dateTime())
        self_main.start_time = self.convertDateTime(self.start_input.dateTime())
        self_main.end_time = self.convertDateTime(self.end_input.dateTime())

        print(f"Start time set to: {self_main.start_time}")

    def videoEndTime(self, self_main):
        self.start_input.setMaximumDateTime(self.end_input.dateTime())
        self_main.start_time = self.convertDateTime(self.start_input.dateTime())
        self_main.end_time = self.convertDateTime(self.end_input.dateTime())
        print(f"End time set to: {self_main.end_time}")

    def showIntersectionSelector(self, self_main):
        self.intersectionSelector = IntersectionSelector(self_main)
        if self.intersectionSelector.exec() == QDialog.Accepted:  # Wait for the dialog to close
            # Retrieve the value from the dialog
            self_main.set_lines(self.intersectionSelector.getSelectedValue())
        else:
            print("Dialog canceled")

    def showIntersectionSavePopup(self, self_main):
        self.intersectionSavePopup = IntersectionSavePopup(self_main)
        if self.intersectionSavePopup.exec() == QDialog.Accepted:  # Wait for the dialog to close
            # Retrieve the value from the dialog
            self_main.save_selected_lines(self.intersectionSavePopup.getSelectedValue()[0], self.intersectionSavePopup.getSelectedValue()[1])
        else:
            print("Dialog canceled")

    def resetIntersection(self):
        pass

    def createIconButton(self, icon_path, callback, width, height, size=32):
        button = QPushButton()
        button.setIcon(QIcon(os.path.join(self.base_path, f"../{icon_path}")))
        button.setIconSize(QPixmap(size, size).size())
        button.setFixedSize(width, height)
        button.setStyleSheet("border: none;")
        button.clicked.connect(callback)
        return button
