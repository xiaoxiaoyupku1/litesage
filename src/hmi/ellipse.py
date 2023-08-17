from PySide6.QtWidgets import (QGraphicsEllipseItem, QGraphicsItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import (QPen, QColor)

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

class WireConnection(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPen(QPen('blue'))
        self.setBrush(QColor('blue'))
        self.lines=[]

    def toPrevJSON(self, centerX, centerY):
        rect = self.rect()
        return [rect.x() - centerX, rect.y() - centerY, rect.width(), rect.width()]

    def make_by_JSON(self, jsn):
        self.setRect(*jsn)
