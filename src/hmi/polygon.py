from PySide6.QtWidgets import (QGraphicsPolygonItem, QGraphicsItem)
from PySide6.QtCore import (Qt, QPointF)
from PySide6.QtGui import (QPen, QColor, QPolygonF)
import json


class Polygon(QGraphicsPolygonItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.pen = self.pen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(self.pen)
        self.last = '_'  # f?


class Pin(Polygon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'pin1'
        self.setPen(QPen('red'))
        self.setBrush(QColor('red'))
        self.design = None

    def check_design(self, design):
        if design is not None:
            if self.collidesWithItem(design.rect):
                design.addPin(self)
                self.setDesign(design)

    def delete(self):
        if self.design is not None:
            self.design.delPin(self)
        self.scene().removeItem(self)

    def setConnected(self):
        pass

    def setDisConnected(self):
        pass

    def getConn(self):
        assert self.design is not None
        return self.design.conns.get(self.name, self.name)

    def updName(self, name):
        if self.design.readonly:
            self.design.conns[self.name] = name
        else:
            oldname = self.name
            idx = self.design.pins.index(oldname)
            self.design.pins[idx] = name
            del self.design.conns[oldname]
            self.design.conns[name] = name
            self.name = name

    def setDesign(self, design):
        self.design = design

    def getParent(self):
        return self.design

    def toPrevJSON(self, centerX, centerY):
        points = []
        scale = self.scene().scale
        distx, disty = [self.x() - centerX, self.y() - centerY]
        for point in self.polygon().toList():
            points.append([(point.x() + distx)*scale, (point.y() + disty)*scale])

        return points

    def make_by_JSON(self, jsn, scene):
        polygonf = QPolygonF()
        for point in jsn:
            polygonf.append(QPointF(point[0] / scene.scale, point[1] / scene.scale))
        self.setPolygon(polygonf)