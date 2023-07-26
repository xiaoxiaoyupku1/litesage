from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsItem)
from PySide6.QtCore import Qt

from src.hmi.dialog import WireDialog
from src.hmi.text import WireNameText
from src.hmi.rect import  SymbolPin

import re

class Line(QGraphicsLineItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.pen = self.pen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(self.pen)

class Bus(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pen.setWidth(4)
        self.setPen(self.pen)

class WireSegment(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pen.setColor('blue')
        self.setPen(self.pen)
        self.pins = set()
        self.text = WireNameText()
        self.wire = None # included in this wire
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
    def addPin(self,pin):
        self.pins.add(pin)
    def removePin(self,pin):
        self.pins.remove(pin)
    def getPins(self):
        return self.pins
    def addPins(self):
        for item in self.collidingItems():
            if type(item) is SymbolPin:
                self.addPin(item)
                item.setOpacity(0)

    def contextMenuEvent(self, event):
        dialog = WireDialog(parent=None, wiresegment=self)
        if dialog.exec():
            self.wire.setName(dialog.name.text())

            if self.text not in self.scene().items():
                self.scene().addItem(self.text)
            self.text.setPos(event.pos())

    def delete(self):
        for pin in self.getPins():
            pin.setOpacity(1)
            pin.parentItem().conns[pin.name] = pin.parentItem().initial_conns[pin.name]
        self.scene().removeItem(self.text)
        self.scene().removeItem(self)
        self.wire.remove(self)
        self.scene().WireList.checkConnectivity(self.wire)

    def isConnected(self, other):

        if not self.collidesWithItem(other):
            return False
        else:
            if self.__getDirection() == other.__getDirection():
                #overlap
                return True
            else:
                if self.__getDirection() == 'x_direct':
                    x=self.line()
                    y=other.line()
                else:
                    x=other.line()
                    y=self.line()
                if y.y1() == x.y1() or y.y2() == x.y1() or x.x1() == y.x1() or x.x2() == y.x1():
                    # ⊥ or ∟
                    return True
                else:
                    #cross
                    return False
    def __getDirection(self):
        if self.line().x1() == self.line().x2():
            return 'y_direct'
        elif self.line().y1() == self.line().y2():
            return 'x_direct'
        else:
            raise Exception("strange line ")

class Wire(): # Wire is a list of WireSegment
    def __init__(self,scene):
        self.scene = scene
        self.segments = []
        self.name = None


    def add(self,segment):
        self.segments.append(segment)
        segment.wire = self

    def moveText(self):
        pass

    def isConnected(self, other):
        for segment in self.getSegments():
            if any(segment.isConnected(other_segment) for other_segment in other.getSegments()):
                return True
        return False

    def getSegments(self):
        return self.segments

    def collidesWithItem(self, item):
        return any(line.collidesWithItem(item) for line in self.getSegments())

    def remove(self, segment):
        self.segments.remove(segment)
        if len(self.getSegments()) == 0:
            self.scene.wireList.remove(self)

    def getPins(self):
        pins = set()
        for segment in self.getSegments():
            pins.update(segment.getPins())
        return pins

    def __setAutoName(self):
        name_nums = [ int(wire.name[3:]) for wire in self.scene.wireList if wire.getName() is not None and re.match('net\d+',wire.getName())]

        id_num = 1
        while id_num in name_nums:
            id_num += 1

        self.setName('net'+str(id_num))

    def getName(self):
        return self.name

    def setName(self,name):
        self.name = name
        self.__updatePinsConn()
        self.__updateSegmentText()

    def __updatePinsConn(self):
        for pin in self.getPins():
            pin.parentItem().conns[pin.name] = self.getName()

    def __updateSegmentText(self):
        for segment in self.getSegments():
            segment.text.setPlainText(self.name)

    def complete(self):
        self.__setAutoName()
        self.__setSelectable()

    def __setSelectable(self):
        for seg in self.getSegments():
            seg.setFlag(QGraphicsItem.ItemIsSelectable, True)

class WireList():
    def __init__(self,scene):
        self.wirelist=[]
        self.scene = scene

    def __iter__(self):
        return self.wirelist.__iter__()

    def __next__(self):
        return self.wirelist.__next__()
    def append(self,new):
        wires_connected = []
        others=[]
        for wire in self.wirelist:
            if new.isConnected(wire):
                wires_connected.append(wire)
            else:
                others.append(wire)

        if len(wires_connected)> 0:
            name = wires_connected[0].getName()
            merged = Wire(self.scene)

            for wire in wires_connected + [new]:
                for segment in wire.getSegments():
                    merged.add(segment)

            merged.setName(name)

            self.wirelist = others + [merged]
        else:
            self.wirelist.append(new)



    def remove(self,wire):
        self.wirelist.remove(wire)

    def checkConnectivity(self,wire):
        pass