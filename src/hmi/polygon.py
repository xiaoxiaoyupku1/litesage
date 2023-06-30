from PySide6.QtWidgets import (QGraphicsPolygonItem, QGraphicsItem)
from PySide6.QtGui import QPen
from PySide6.QtCore import Qt

class Polygon(QGraphicsPolygonItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.pen = QPen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(self.pen)