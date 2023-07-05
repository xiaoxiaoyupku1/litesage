from PySide6.QtWidgets import (QGraphicsItemGroup,QGraphicsItem)
from PySide6.QtGui import QPen
from PySide6.QtCore import Qt


class Group(QGraphicsItemGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def paint(self, painter, option, widget=None,  *args, **kwargs):
        if self.isSelected():
            pen = QPen()
            pen.setStyle(Qt.DotLine)
            pen.setWidth(pen.width()/2)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())