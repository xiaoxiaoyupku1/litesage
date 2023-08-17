from PySide6.QtWidgets import (QGraphicsRectItem, QGraphicsItem)
from PySide6.QtCore import Qt
from src.hmi.dialog import DesignDialog

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
        self.pen.setStyle(Qt.DotLine)
        self.setPen(self.pen)
        self.design = None

    def setDesign(self, design):
        self.design = design

    def delete(self):
        if self.design is not None:
            self.design.delete()


    def contextMenuEvent(self, event):
        if self.design is None:
            return

        dialog = DesignDialog(parent=None,designRect=self)
        dialog.exec()


class SymbolPin(Rect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pen.setColor('red')
        self.setPen(self.pen)
        self.name = None
        self.parent = None
        self.status = False
    def setName(self,name):
        self.name = name

    def setConnected(self):
        self.setOpacity(0)
        self.status = True

    def setDisConnected(self):
        self.setOpacity(1)
        self.status = False

    def setParent(self, parent):
        self.parent = parent

    def getParent(self):
        return self.parent

    def getConn(self):
        assert self.parent is not None
        return self.parent.conns.get(self.name, self.name)