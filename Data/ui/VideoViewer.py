from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)


class ClickablePixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, callback, lineEditor_click):
        super().__init__(pixmap)
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.callback = callback
        self.lineEditor_click = lineEditor_click

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            relative_pos = event.pos()
            self.lineEditor_click(int(relative_pos.x()), int(relative_pos.y()))
            print(f"Clicked at relative position: {relative_pos.x()}, {relative_pos.y()}")
            self.callback()
        event.accept()

class VideoViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

    def setPixmap(self, image, show_frame_callback = None, lineEditor_click = None):
        self.scene.clear()
        pixmap = QPixmap.fromImage(image)
        if not show_frame_callback or not lineEditor_click:
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
        else:
            self.pixmap_item = ClickablePixmapItem(pixmap, show_frame_callback, lineEditor_click)
        self.scene.addItem(self.pixmap_item)
        self.setSceneRect(self.pixmap_item.boundingRect())

