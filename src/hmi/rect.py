from PySide6.QtWidgets import (QGraphicsRectItem, QGraphicsItem)
from PySide6.QtGui import QPen
from PySide6.QtCore import Qt

class Rect(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.pen = QPen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(self.pen)


class DesignBorder(Rect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pen.setWidth(8)
        self.pen.setColor('green')
        self.setPen(self.pen)