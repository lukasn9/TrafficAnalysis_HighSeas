from PySide6.QtWidgets import QDateTimeEdit
from PySide6.QtCore import QDateTime

class Calendar(QDateTimeEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setCalendarPopup(True)

        self.calendar_widget = self.calendarWidget()
        self.calendar_widget.setFixedSize(400, 300)
        self.calendar_widget.setStyleSheet("""
            QCalendarWidget {
                background-color: #2e3440;
                border: 1px solid #88c0d0;
                color: #eceff4;
                font-size: 14px;
            }

            QCalendarWidget QToolButton {
                background-color: #4c566a;
                color: #d8dee9;
                border: none;
                font-size: 18px;
                height: 40px;
                width: 120px;
                margin: 2px;
                border-radius: 5px;
            }

            QCalendarWidget QToolButton:hover {
                background-color: #88c0d0;
            }

            QCalendarWidget QToolButton::pressed {
                background-color: #454e57;
            }

            QCalendarWidget QAbstractItemView {
                selection-background-color: #5e81ac;
                selection-color: #eceff4;
            }

            QCalendarWidget QSpinBox {
                margin: 2px;
                background-color: #3b4252;
                color: #eceff4;
                font-size: 16px;
                height: 35px;
                width: 70px;
            }

            QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button {
                width: 20px;
                height: 20px;
            }

            QCalendarWidget QSpinBox::up-button:hover, QCalendarWidget QSpinBox::down-button:hover {
                background-color: #88c0d0;
            }

            QCalendarWidget QSpinBox::up-arrow, QCalendarWidget QSpinBox::down-arrow {
                width: 10px;
                height: 10px;
            }
        """)

        self.setDateTime(QDateTime.currentDateTime())