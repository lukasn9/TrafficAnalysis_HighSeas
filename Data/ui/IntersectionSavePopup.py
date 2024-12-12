from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
import os


class IntersectionSavePopup(QDialog):
    def __init__(self, self_main):
        super().__init__()
        self.setGeometry(200, 400, 500, 300)
        self.setWindowTitle("Save line configuration")

        if self_main.dark_theme:
            icon_path = "../icons/icon-dark.ico"
        else:
            icon_path = "../icons/icon-light.ico"

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(self.base_path, icon_path)))

        self.line_inputs = []

        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        intersection_label = QLabel("Configuration Name")
        intersection_label.setObjectName("intersection_save_name")
        intersection_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.intersection_name_input = QTextEdit()
        self.intersection_name_input.setPlaceholderText("Name of the configuration")
        self.intersection_name_input.setStyleSheet("border: 1px solid #aaaaaa; border-radius: 5px; padding: 5px; width: 80px; height: 30px; margin-bottom: 10px;")

        intersection_list_widget = QWidget()
        intersection_list_layout = QVBoxLayout(intersection_list_widget)

        intersection_list_layout.addWidget(intersection_label)
        intersection_list_layout.addWidget(self.intersection_name_input)

        for i in range(len(self_main.lineEditor.lines)):
            item_widget = self.createItemWidget(i)
            intersection_list_layout.addWidget(item_widget)

        intersection_list_widget.setLayout(intersection_list_layout)
        scroll_area.setWidget(intersection_list_widget)

        main_layout.addWidget(scroll_area)
        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(lambda: self.saveIntersectionLines())
        confirm_button.setObjectName("save_intersection_button")
        main_layout.addWidget(confirm_button)
    def getSelectedValue(self):
        # Retrieve the main intersection name
        intersection_name = self.intersection_name_input.toPlainText()

        # Retrieve all the line inputs' values
        line_names = [line_input.toPlainText() for line_input in self.line_inputs]
        return (intersection_name, line_names)
    def createItemWidget(self, index):
        item_widget = QWidget()
        item_widget.setStyleSheet("background-color: #3D3D3D; border-radius: 5px;")
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(10, 10, 10, 10)
        item_layout.setSpacing(5)

        intersection_label = QLabel(f"Line {index + 1} Name")
        intersection_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        intersection_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        line_name_input = QTextEdit()
        line_name_input.setPlaceholderText("Name of the line")
        line_name_input.setStyleSheet("border: 1px solid #aaaaaa; border-radius: 5px; padding: 5px; width: 100px; height: 30px;")

        self.line_inputs.append(line_name_input)


        item_layout.addWidget(intersection_label)
        item_layout.addWidget(line_name_input)

        return item_widget
    def saveIntersectionLines(self):
        self.accept()
