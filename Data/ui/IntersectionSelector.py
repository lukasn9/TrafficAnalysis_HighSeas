from PySide6.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QFrame, QPushButton, QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os
from ..core.Saving import get_line_configs

class IntersectionSelector(QDialog):
    def __init__(self, self_main):
        super().__init__()
        self.setGeometry(200, 400, 500, 300)
        self.setWindowTitle("Choose a line configuration")

        if self_main.dark_theme:
            icon_path = "../icons/icon-dark.ico"
        else:
            icon_path = "../icons/icon-light.ico"

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(self.base_path, icon_path)))

        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        intersection_list_widget = QWidget()
        intersection_list_layout = QVBoxLayout(intersection_list_widget)

        for config in get_line_configs(self_main.krizovatka):
            item_button = self.createItemButton(config.removesuffix('.json'), config)
            intersection_list_layout.addWidget(item_button)

        intersection_list_widget.setLayout(intersection_list_layout)
        scroll_area.setWidget(intersection_list_widget)

        main_layout.addWidget(scroll_area)

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