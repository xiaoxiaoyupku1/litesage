from PySide6.QtWidgets import (QGraphicsRectItem, QGraphicsItem)

class Rect(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)