from PySide6.QtWidgets import (QGraphicsRectItem, QGraphicsItem)
from PySide6.QtCore import Qt

class Rect(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.pen = self.pen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(self.pen)


class DesignBorder(Rect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pen.setWidth(8)
        self.pen.setColor('green')
        self.setPen(self.pen)


class SymbolPin(Rect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pen.setColor('red')
        self.setPen(self.pen)
        self.name = None
    def setName(self,name):
        self.name = name