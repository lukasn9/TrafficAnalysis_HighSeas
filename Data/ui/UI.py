import cv2
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
                               QWidget, QFileDialog, QSlider, QLabel, QGraphicsView, QGraphicsScene, QSpacerItem,
                               QSizePolicy, QAbstractSpinBox, QSpinBox, QMessageBox, QComboBox, QGraphicsPixmapItem)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QPixmap, QImage, QDesktopServices
import urllib3

class ClickablePixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, callback):
        super().__init__(pixmap)
        # Enable mouse tracking on the item
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.callback = callback  # Store the callback

    def mousePressEvent(self, event):
        # Check if the click is within the pixmap area
        if event.button() == Qt.LeftButton:
            # Calculate the position relative to the pixmap
            relative_pos = event.pos()
            LineEditor.mouse_callback(int(relative_pos.x()), int(relative_pos.y()))
            print(f"Clicked at relative position: {relative_pos.x()}, {relative_pos.y()}")
            self.callback()  # Trigger the showFrame method

        event.accept()

class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)


    def setPixmap(self, image, show_frame_callback):
        # Load a pixmap and add it to the scene
        self.scene.clear()

        pixmap = QPixmap.fromImage(image)
       # pixmap = pixmap.scaled(640, 360, Qt.KeepAspectRatio)
        self.pixmap_item = ClickablePixmapItem(pixmap, show_frame_callback)
        self.scene.addItem(self.pixmap_item)
        # Center the view on the pixmap and set the scene rectangle
        self.setSceneRect(self.pixmap_item.boundingRect())
class MainWindow(QMainWindow):
    def __init__(self, lineEditor, start):
        super().__init__()
        self.setWindowTitle("Intersection Traffic Analysis")
        self.setGeometry(100, 100, 800, 600)
        global LineEditor
        LineEditor = lineEditor
        self.current_view = None
        self.video_path = None
        self.cap = None
        self.frame_count = 0
        self.local_analysis = False
        self.data_sending_freq = 2
        self.selected_model = "quick_analysis"
        self.slider = None
        self.scene = None
        self.view = None
        self.traffic_analysis = None
        self.initUI()
        self.start = start
    def check_internet_conn(self, freq_inp):
        try:
            self.local_analysis = False
            http = urllib3.PoolManager(timeout=3.0)
            r = http.request('GET', 'aidetection.great-site.net', preload_content=False)
            code = r.status
            r.release_conn()
            if code == 200:
                return True
        except:
            internet_warning = QMessageBox(self)
            internet_warning.setWindowTitle("Can't Connect to the Internet")
            internet_warning.setText("There has been an issue with sending data to the server.")
            retry_button = internet_warning.addButton("Retry", QMessageBox.AcceptRole)
            internet_warning.addButton("Analyze Locally", QMessageBox.RejectRole)
            internet_warning.exec()

            if internet_warning.clickedButton() == retry_button:
                self.check_internet_conn(freq_inp)
            else:
                self.local_analysis = True
                freq_inp.setValue(0)
                freq_inp.setEnabled(False)
                freq_inp.setObjectName("freq_inp_disabled")
                freq_inp.setStyleSheet("color: #373737;")
            return False

    def updateModelSelection(self, model):
        model = model.lower().replace(" ", "_")
        self.selected_model = model

    def initUI(self):
        self.showModeSelectorView()

    def createIconButton(self, icon_path, size=32):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QPixmap(size, size).size())
        button.setFixedSize(40, 40)
        button.setStyleSheet("border: none;")
        return button

    def createNavBar(self):
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_widget.setFixedWidth(60)

        nav_widget.setStyleSheet("background-color: #313131;")

        self.start_button = self.createIconButton("icons/play.png")
        self.stop_button = self.createIconButton("icons/stop.png")
        self.quit_button = self.createIconButton("icons/exit.png")

        start_layout = QHBoxLayout()
        start_layout.addStretch()
        start_layout.addWidget(self.start_button)
        start_layout.addStretch()

        stop_layout = QHBoxLayout()
        stop_layout.addStretch()
        stop_layout.addWidget(self.stop_button)
        stop_layout.addStretch()

        quit_layout = QHBoxLayout()
        quit_layout.addStretch()
        quit_layout.addWidget(self.quit_button)
        quit_layout.addStretch()

        nav_layout.addLayout(start_layout)
        nav_layout.addLayout(stop_layout)
        nav_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        nav_layout.addLayout(quit_layout)

        self.quit_button.clicked.connect(self.close)

        return nav_widget

    def showModeSelectorView(self):
        if self.current_view:
            self.current_view.deleteLater()

        self.current_view = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        nav_widget = self.createNavBar()

        content_layout = QVBoxLayout()

        process_live_button = QPushButton("Process Live Footage")
        process_live_button.setObjectName("process_live_button")

        process_video_button = QPushButton("Process a Video File")
        process_video_button.setObjectName("process_video_button")

        website_button = QPushButton("Web")
        website_button.setObjectName("website_button")
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aidetection.great-site.net/")))

        content_layout.addWidget(website_button, alignment=Qt.AlignTop | Qt.AlignRight)
        content_layout.addStretch()
        content_layout.addWidget(process_live_button, alignment=Qt.AlignCenter)
        content_layout.addWidget(process_video_button, alignment=Qt.AlignCenter)
        content_layout.addStretch()

        #process_live_button.clicked.connect(self.showLiveConnectionView())
        process_video_button.clicked.connect(self.showVideoSelectorView)

        main_layout.addWidget(nav_widget)
        main_layout.addLayout(content_layout, 4)

        self.current_view.setLayout(main_layout)
        self.setCentralWidget(self.current_view)

    def showVideoSelectorView(self):
        if self.current_view:
            self.current_view.deleteLater()

        self.current_view = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        nav_widget = self.createNavBar()

        top_bar = QHBoxLayout()
        content_layout = QVBoxLayout()

        select_file_button = QPushButton("Select a File to Process")
        select_file_button.setObjectName("select_file_button")
        select_file_button.setFixedSize(200, 50)

        website_button = QPushButton("Web")
        website_button.setObjectName("website_button")
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aidetection.great-site.net/")))

        back_button = self.createIconButton("icons/back.png")
        back_button.setFixedSize(70, 70)
        back_button.clicked.connect(self.showModeSelectorView)

        top_bar.addWidget(back_button, alignment=Qt.AlignTop | Qt.AlignLeft)
        top_bar.addWidget(website_button, alignment=Qt.AlignTop | Qt.AlignRight)

        content_layout.addLayout(top_bar)

        center_layout = QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(select_file_button, alignment=Qt.AlignCenter)
        center_layout.addStretch()

        content_layout.addLayout(center_layout)

        select_file_button.clicked.connect(self.selectFile)

        main_layout.addWidget(nav_widget)
        main_layout.addLayout(content_layout, 4)

        self.current_view.setLayout(main_layout)
        self.setCentralWidget(self.current_view)


    def selectFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select an MP4 File", "", "MP4 Files (*.mp4)")
        if file_name:
            self.video_path = file_name
            self.cap = cv2.VideoCapture(self.video_path)
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            ret, frame = self.cap.read()
            image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(image)
            self.showLineSelectionView()

    def showLineSelectionView(self):
        self.local_analysis = False
        
        if self.current_view:
            self.current_view.deleteLater()

        self.current_view = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        nav_widget = self.createNavBar()

        content_layout = QVBoxLayout()

        settings_bar = QHBoxLayout()
        label = QLabel("Data Upload Frequency (s)")
        label.setStyleSheet("font-size: 14px; font-weight: bold;")

        back_button = self.createIconButton("icons/back.png")
        back_button.setFixedSize(70, 70)
        back_button.clicked.connect(self.showVideoSelectorView)

        settings_bar.addWidget(back_button, alignment=Qt.AlignTop | Qt.AlignLeft)

        frequency_input = QSpinBox()
        frequency_input.setMinimum(0)
        frequency_input.setMaximum(99)
        frequency_input.setValue(2)
        frequency_input.setButtonSymbols(QAbstractSpinBox.NoButtons)
        if self.local_analysis ==  False:
            frequency_input.setObjectName("freq_inp")

        modelSelector = QComboBox()
        modelSelector.addItem("Quick Analysis")
        modelSelector.addItem("Accurate Analysis")
        modelSelector.setObjectName("modelSelector")
        modelSelector.currentIndexChanged.connect(lambda: self.updateModelSelection(modelSelector.currentText()))

        self.view = GraphicsView()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(0)
        self.slider.setMaximum(self.frame_count - 1)
        self.slider.setEnabled(True)

        website_button = QPushButton("Web")
        website_button.setObjectName("website_button")
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aidetection.great-site.net/")))

        settings_bar.addWidget(label)
        settings_bar.addWidget(frequency_input)
        settings_bar.addWidget(modelSelector)
        settings_bar.addStretch()
        settings_bar.addWidget(website_button)

        content_layout.addLayout(settings_bar)
        content_layout.addWidget(self.view)
        content_layout.addWidget(self.slider)

        self.showFrame()
        self.slider.valueChanged.connect(lambda: self.showFrame())

        main_layout.addWidget(nav_widget)
        main_layout.addLayout(content_layout, 4)

        self.current_view.setLayout(main_layout)
        self.setCentralWidget(self.current_view)

        self.check_internet_conn(frequency_input)

        if self.local_analysis:
            label.setStyleSheet("color: #373737; font-size: 14px; font-weight: bold;")
        else:
            label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")

        self.start_button.clicked.connect(lambda: self.showAnalysisView())

    def showAnalysisView(self):
        self.local_analysis = False
        
        if self.current_view:
            self.current_view.deleteLater()

        self.current_view = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        nav_widget = self.createNavBar()

        content_layout = QVBoxLayout()

        info_bar = QHBoxLayout()

        self.view = GraphicsView()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(0)
        self.slider.setMaximum(self.frame_count - 1)
        self.slider.setEnabled(False)

        website_button = QPushButton("Web")
        website_button.setObjectName("website_button")
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://aidetection.great-site.net/")))


        info_bar.addStretch()
        info_bar.addWidget(website_button)

        content_layout.addLayout(info_bar)
        content_layout.addWidget(self.view)
        content_layout.addWidget(self.slider)

        self.showFrame()

        main_layout.addWidget(nav_widget)
        main_layout.addLayout(content_layout, 4)

        self.current_view.setLayout(main_layout)
        self.setCentralWidget(self.current_view)

        self.start()

    def updateFrequency(self, frequency_input):

        self.data_sending_freq = frequency_input.value()

    def showFrame(self, frame=None, current_frame=0):
        if frame is None:
            frame_idx = self.slider.value()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = self.cap.read()
        else:
            self.slider.setValue(current_frame)
        LineEditor.change_image(frame)
        frame = LineEditor.image
        image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_BGR888)
        self.view.setPixmap(image, self.showFrame)