from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsItem)
from PySide6.QtCore import Qt

class Line(QGraphicsLineItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.pen = self.pen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(self.pen)

class Bus(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pen.setWidth(4)
        self.setPen(self.pen)