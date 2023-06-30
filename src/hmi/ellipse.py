from PySide6.QtWidgets import (QGraphicsEllipseItem, QGraphicsItem)
from PySide6.QtCore import Qt

class Circle(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

class Arc(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def paint(self, painter, option, widget):
        pen = self.pen()
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(self.brush())
        painter.drawArc(self.rect(), self.startAngle(), self.spanAngle())