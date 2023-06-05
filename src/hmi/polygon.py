from PySide6.QtWidgets import (QGraphicsPolygonItem, QGraphicsItem)

class Polygon(QGraphicsPolygonItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)