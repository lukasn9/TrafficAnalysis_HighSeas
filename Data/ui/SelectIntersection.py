from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QScrollArea, QFrame, QPushButton, QLabel, QWidget, QHBoxLayout, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os
from ..core.Saving import get_line_configs

class SelectIntersection(QDialog):
    def __init__(self, self_main):
        super().__init__()
        self.self_main = self_main
        self.line_path = None
        self.setGeometry(200, 400, 500, 300)
        self.setWindowTitle("Create or choose an intersection")

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = "../icons/icon-dark.ico" if self_main.dark_theme else "../icons/icon-light.ico"
        self.setWindowIcon(QIcon(os.path.join(self.base_path, icon_path)))

        self.main_layout = QVBoxLayout(self)
        self.showMenu()

    def showMenu(self):
        self.clearLayout(self.main_layout)

        create_button = QPushButton("Create New Intersection")
        create_button.clicked.connect(self.createNewIntersection)
        create_button.setObjectName("create_button")

        show_button = QPushButton("Show Intersections")
        show_button.clicked.connect(self.showIntersectionList)
        show_button.setObjectName("show_button")

        self.main_layout.addWidget(create_button)
        self.main_layout.addWidget(show_button)

    def showIntersectionList(self):
        self.clearLayout(self.main_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        intersection_list_widget = QWidget()
        intersection_list_layout = QVBoxLayout(intersection_list_widget)

        for config in get_line_configs(self.self_main.krizovatka):
            item_button = self.createItemButton(config.removesuffix('.json'), config)
            intersection_list_layout.addWidget(item_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.showMenu)
        back_button.setObjectName("select_back_button")
        intersection_list_layout.addWidget(back_button)

        intersection_list_widget.setLayout(intersection_list_layout)
        scroll_area.setWidget(intersection_list_widget)

        self.main_layout.addWidget(scroll_area)

    def createNewIntersection(self):
        self.clearLayout(self.main_layout)

        input_label = QLabel("Enter Intersection Name:")
        input_label.setObjectName("input_label")
        intersection_name_input = QLineEdit()

        create_button = QPushButton("Create")
        create_button.setObjectName("select_create_button")
        create_button.clicked.connect(lambda: self.saveNewIntersection(intersection_name_input.text()))

        back_button = QPushButton("Back")
        back_button.setObjectName("select_back_button")
        back_button.clicked.connect(self.showMenu)

        self.main_layout.addWidget(input_label)
        self.main_layout.addWidget(intersection_name_input)
        self.main_layout.addWidget(create_button)
        self.main_layout.addWidget(back_button)

    def saveNewIntersection(self, name):
        if name.strip():
            print(f"New intersection created: {name}")
            self.accept()

    def createItemButton(self, intersection_name, data_path):
        button = QPushButton()
        button.clicked.connect(lambda: self.loadIntersectionLines(data_path))
        button.setObjectName("intersection_item")
        button.setFixedSize(440, 80)
        button.setStyleSheet("text-align: center; border: none;")

        item_layout = QHBoxLayout(button)
        item_layout.setContentsMargins(10, 0, 0, 0)

        intersection_label = QLabel(intersection_name)
        intersection_label.setObjectName("history_name")
        intersection_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        item_layout.addWidget(intersection_label, stretch=1)
        item_layout.addStretch()

        button.setLayout(item_layout)
        return button

    def getSelectedValue(self):
        return self.line_path

    def loadIntersectionLines(self, data_path):
        self.line_path = data_path
        self.accept()

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
