from PySide6.QtWidgets import (QGraphicsEllipseItem, QGraphicsItem)

class Circle(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)