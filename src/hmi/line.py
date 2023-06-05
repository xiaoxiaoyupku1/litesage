from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsItem)

class Line(QGraphicsLineItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)