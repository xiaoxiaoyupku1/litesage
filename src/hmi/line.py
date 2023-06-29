from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsItem)
from PySide6.QtGui import QPen
# from PySide6.QtCore import Qt

class Line(QGraphicsLineItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        # pen = QPen()
        # pen.setJoinStyle(Qt.RoundJoin)
        # self.setPen(pen)

class Bus(QGraphicsLineItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        pen = QPen()
        pen.setWidth(4)
        # pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)