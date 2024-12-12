import re
import sys
from asyncio import sleep
from pathlib import Path

import cv2
from PySide6.QtCore import QCoreApplication, QTimer
from qasync import QEventLoop
from PySide6.QtCore import QThread, Signal

from PySide6.QtGui import QImage, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from Data.core.vehicle_detection_tracking import TrafficAnalysis
import asyncio
import datetime
from Data.core.LineEditor import LineEditor
from Data.core.Connection import send_data, get_places, create_place, check_availability, delete_logs, check_live, set_live
import threading
import traceback
import sys
from Data.core.Saving import save_lines, get_lines, save_data_analysis, get_data, save_history, get_history
from Data.core.GetTheme import is_dark_mode
from Data.ui.AnalysisView import AnalysisView
from Data.ui.LineSelection import LineSelectionView
from Data.ui.ModeSelector import ModeSelectorView
from Data.ui.NavBar import NavBar
from Data.ui.VideoSelector import VideoSelectorView
from Data.ui.HistoryView import HistoryView
from Data.ui.VideoPlayback import VideoPlayback
from Data.ui.VideoPlaybackNavBar import VideoPlaybackNavBar

VIDEOS = {
    "st-marc-camera": "Videos/stmarc_video.avi",
    "dialnica": "Videos/3.mp4",
    "sancova1": "Videos/sancova.mp4",
    "Sancova": "Data/assets/Videos/sancova2.mp4",
    "sancova3": "Videos/sancova3.mp4",
}



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("main_window")
        self.dark_theme = is_dark_mode()
        self.icon_path = "Data/icons/icon-dark.ico" if self.dark_theme else "Data/icons/icon-light.ico"
        self.stop = None
        self.setWindowTitle("Intersection Traffic Analysis")
        self.setGeometry(100, 100, 1200, 600)
        self.current_view = None
        self.video_path = None
        self.data_path = None
        self.output_path = None
        self.cap = None
        self.frame_count = 0
        self.fps = 0
        self.local_analysis = False
        self.start_enabled = False
        self.stop_enabled = False
        self.data_sending_freq = 2
        self.fast_model = True
        self.traffic_analysis = None
        self.krizovatka = "Sancova"
        self.start_time = None
        self.end_time = None
        self.analysis_start_time = None
        self.realtime = False
        self.send_period_s = 2
        self.live_cam = 0
        self.pause_condition = threading.Condition()
        self.pause = False

        icon = QIcon(self.icon_path)
        self.setWindowIcon(icon)

        # Main layout
        main_widget = QWidget()
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Fixed navigation bar
        self.nav_widget = NavBar( self.showAnalysisView, self.stop_analysis,  self.closeCallback)
        self.main_layout.addWidget(self.nav_widget)

        # Placeholder for central widget area
        self.central_widget_area = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget_area)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.central_widget_area, 1)

        # Set the main widget as the central widget of the window
        self.setCentralWidget(main_widget)
        self.initUI()

        #   lines = get_lines(self.krizovatka, "1")
        self.street_names = []
        self.lineEditor = LineEditor(self.nav_widget.toogle_startButton)



    def initUI(self):
        self.showModeSelectorView()

    def closeCallback(self):
        print("close")
        self.close()

    def historyCloseCallback(self, graphView):
        print("close")
        self.close()
        graphView.close()

    def showModeSelectorView(self):
        self.changeView(ModeSelectorView(self.showVideoSelectorView, self.showHistoryView, self))

    def setVideoData(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.realtime:
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.video_end = self.frame_count / self.fps
    def showHistoryView(self):
        if self.nav_widget:
            self.nav_widget.deleteLater()

        self.nav_widget = NavBar( self.showAnalysisView, self.stop_analysis,  self.closeCallback)

        self.main_layout.insertWidget(0, self.nav_widget)
        self.changeView(HistoryView(self.showModeSelectorView, self))

    def showVideoSelectorView(self, live):
        if not live:
            self.changeView(
                VideoSelectorView(self.showLineSelectionView, self.showModeSelectorView, self.setVideoData, self))
        else:
            self.realtime = True
            self.setVideoData(0)

            self.changeView(LineSelectionView(self.showVideoSelectorView,
                                                  self.updateFrequency, self.showFrame, self.frame_count,
                                                  self.fps, self.local_analysis, True, self))
            self.showFrame()

    def showLineSelectionView(self):
        self.changeView(LineSelectionView(self.showVideoSelectorView,
                                          self.updateFrequency, self.showFrame, self.frame_count,
                                          self.fps, self.local_analysis, False, self))
        self.showFrame()

    def showAnalysisView(self):
        self.start_analysis()

    def showVideoPlaybackView(self, output_path, data_path):
        if self.realtime:
            self.changeView(ModeSelectorView(self.showVideoSelectorView, self.showHistoryView, self))
            return
        if self.nav_widget:
            self.nav_widget.deleteLater()

        self.nav_widget = VideoPlaybackNavBar(self, None)

        self.main_layout.insertWidget(0, self.nav_widget)

        self.changeView(VideoPlayback(output_path, data_path, self))


    def changeView(self, new_view):
        if self.current_view:
            self.current_view.deleteLater()

        self.current_view = new_view
        self.central_layout.addWidget(self.current_view)
        QApplication.processEvents()

    def showFrame(self, frame=None, current_frame=0):
        if frame is None:
            if not self.realtime:
                frame_idx = self.current_view.slider.value()
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = self.cap.read()
        else:
            self.current_view.slider.setValue(current_frame)
            image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_BGR888)
            self.current_view.viewer.setPixmap(image)
            return

        self.lineEditor.change_image(frame)
        frame = self.lineEditor.image
        image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_BGR888)
        self.current_view.viewer.setPixmap(image, self.showFrame, self.lineEditor.mouse_callback)

    def updateFrequency(self, value):
        self.data_upload_frequency = value
        print(f"Data upload frequency set to: {value}")

    def handleExceptions(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Application Error")
        msg_box.setText("An unexpected error occurred.")
        msg_box.setInformativeText("The application will now close.")
        msg_box.setDetailedText(error_message)
        msg_box.setStandardButtons(QMessageBox.Close)
        quit_button = msg_box.button(QMessageBox.Close)
        quit_button.setText("Quit")
        msg_box.setWindowIcon(QIcon("Data/icons/icon.ico"))
        msg_box.exec()

        QApplication.quit()


    async def run_cv(self):
        while True:
            data = self.traffic_analysis.get_accumulated_values()
            if not self.realtime:

                await save_data_analysis(data, self.data_path, self.krizovatka, Path(self.video_path).name, self.start_time,
                               self.end_time, self.analysis_start_time)

                await save_history(self.output_path, self.data_path, self.krizovatka, Path(self.output_path).name, self.start_time, self.end_time,
                         self.analysis_start_time)

            if self.local_analysis:
                match await send_data(data, self.krizovatka, self.toggle_pause):
                    case 1:
                        self.local_analysis = True
                        break
                    case 2:
                        self.stop_analysis()
                        break
            await asyncio.sleep(self.send_period_s)


    async def analysis(self):
        current_frame = 0
        if not self.realtime:
            duration = (self.end_time - self.start_time).total_seconds()
            sec_per_frame = duration / self.frame_count
        while True:
            #with self.pause_condition:
               # while self.pause:
               #     self.pause_condition.wait()
            current_time = self.start_time + datetime.timedelta(seconds=round(sec_per_frame * current_frame)) if not self.realtime else datetime.datetime.now()
            if self.traffic_analysis.update_scan_frame(current_time) or self.stop:
                self.traffic_analysis.release_resources()
                self.stop = False
                self.showVideoPlaybackView(self.output_path, self.data_path)
                break
            if not self.traffic_analysis.current_frame is None:
                self.showFrame(self.traffic_analysis.current_frame, current_frame)
            current_frame += 1
    def set_lines(self, path):
        lines = get_lines(self.krizovatka, path)
        self.lineEditor.lines = list(lines.values())
        self.lineEditor.names = list(lines.keys())
        print(self.lineEditor.lines, self.lineEditor.names)

        self.showFrame()
    def save_selected_lines(self, name, line_names):
        data = {}
        for i in range(len(line_names)):
            data[line_names[i]] = self.lineEditor.lines[i]
        save_lines(data, self.krizovatka, name)
        self.street_names = data.keys()
    def toggle_pause(self, toggle):
        with self.pause_condition:
            self.pause = toggle
            if not self.pause:
                self.pause_condition.notify_all()
    def start_analysis(self):
        self.analysis_start_time = datetime.datetime.now()
        if not self.realtime:
            self.output_path = re.sub(r'[<>:"|?*]', '_',f"Data/assets/intersections/{self.krizovatka}/outputs/{Path(self.video_path).stem}-{self.analysis_start_time.isoformat().replace(':', '-')}.mp4")
            self.data_path = re.sub(r'[<>:"|?*]', '_',f"Data/assets/intersections/{self.krizovatka}/data/{Path(self.video_path).stem}-{self.analysis_start_time.isoformat().replace(':', '-')}.json")
        print(self.data_path)
        #   save_lines(self.lineEditor.lines, self.krizovatka, "1")
        self.traffic_analysis = TrafficAnalysis(self.live_cam if self.realtime else self.video_path, self.output_path,
                                                self.lineEditor.lines,
                                                self.street_names, self.fast_model)
        self.nav_widget.toogle_startButton(False)
        self.nav_widget.toogle_stopButton(True)
        sendSave_data_thread = threading.Thread(target=asyncio.run, args=(self.run_cv(),), daemon=True)
        sendSave_data_thread.start()



        self.changeView(AnalysisView(self.showLineSelectionView, self.showFrame, self.frame_count, self))
        QTimer.singleShot(0, lambda: asyncio.run(self.analysis()))



    def stop_analysis(self):
        self.stop = True
        self.nav_widget.toogle_stopButton(False)

   # sys.excepthook = handleExceptions

if __name__ == "__main__":
    # print(get_places())
    # create_place("Štefánikoľ vsdda", 48, 17)

    app = QApplication(sys.argv)
    with open("Data/ui/style.qss", "r") as file:
        app.setStyleSheet(file.read())

    window = MainWindow()

    window.show()

    sys.exit(app.exec())
