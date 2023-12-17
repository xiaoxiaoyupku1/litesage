from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsItem)
from PySide6.QtCore import Qt,QLineF
from PySide6.QtWidgets import ( QGraphicsScene )

from src.hmi.dialog import WireDialog
from src.hmi.text import WireNameText
from src.hmi.rect import  SymbolPin
from src.hmi.polygon import Pin
from src.hmi.ellipse import WireConnection

import math


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
        self.pins = set() #SymbolPins or Pins (design)
        self.text = WireNameText()
        self.wire = None # included in this wire
        self.connections = []

        self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def addPin(self,pin):
        self.pins.add(pin)
    def removePin(self,pin):
        self.pins.remove(pin)
    def getPins(self):
        return self.pins
    def addPins(self):
        for item in self.collidingItems():
            if isinstance(item, SymbolPin) or isinstance(item, Pin):
                self.addPin(item)
                item.setConnected()


    def contextMenuEvent(self, event):
        self.scene().cleanCursorSymb()
        dialog = WireDialog(parent=None, wiresegment=self)
        if dialog.exec():
            netName = dialog.name.text().strip()
            self.wire.setName(netName)
            for xpin in self.getPins():
                if isinstance(xpin, Pin):
                    xpin.updName(netName)

            if self.text not in self.scene().items():
                self.scene().addItem(self.text)
            self.text.setPos(event.pos())

    def delete(self):
        for conn in self.connections:
            self.scene().removeItem(conn)
        self.connections = []

        for pin in self.getPins():
            pin.setDisConnected()
            pin.getParent().conns[pin.name] = pin.getParent().initial_conns[pin.name]
        self.scene().removeItem(self.text)
        self.scene().removeItem(self)
        self.wire.remove(self)
        self.wire.parent.wireList.checkConnectivity(self.wire)

    def same(self,p1,p2):
        return math.isclose(p1.x(),p2.x()) and math.isclose(p1.y(), p2.y())

    def isoverlap(self, other):
        return self.__getDirection() == other.__getDirection()


    def isConnected(self, other):

        if not self.collidesWithItem(other):
            #case 1: no intersection
            return False
        else:
            if self.isoverlap(other):
                #case 2: overlap
                return True
            else:
                if self.same(self.line().p1(), other.line().p1()) or self.same(self.line().p2(), other.line().p1()) or self.same(self.line().p1(), other.line().p2()) or self.same(self.line().p2(), other.line().p2()):
                    # case 3: ∟
                    return True

                else:
                    if self.__getDirection() == 'horizontal':
                        hori=self.line()
                        verti=other.line()
                    else:
                        hori=other.line()
                        verti=self.line()


                    if math.isclose(verti.y1(), hori.y1()) or math.isclose(verti.y2(), hori.y1()) or math.isclose(hori.x1(), verti.x1()) or math.isclose(hori.x2(), verti.x1()):
                        #case 4: ⊥
                        self.__drawConnection(other)
                        return True
                    else:
                        #case 5: crossover
                        return False

    def __drawConnection(self,other):
        _, p = self.line().intersects(other.line())
        r = 25 / self.scene().scale
        connection = WireConnection(p.x()-r, p.y()-r, r*2, r*2)
        self.scene().addItem(connection)
        self.connections.append(connection)
        other.connections.append(connection)
        connection.lines.append(self)
        connection.lines.append(other)

    def __getDirection(self):
        if self.line().x1() == self.line().x2():
            return 'vertical'
        elif self.line().y1() == self.line().y2():
            return 'horizontal'
        else:
            raise Exception("strange line ")
    def toPrevJSON(self, centerX, centerY):
        line = self.line()
        items = [line.x1() - centerX, line.y1() - centerY, line.x2() - centerX, line.y2() - centerY]
        return items
    def make_by_JSON(self,jsn):
        self.setLine(QLineF(*jsn))

class Wire(): # Wire is a list of WireSegment
    def __init__(self,parent):
        self.parent = parent #scene or design
        self.segments: list[WireSegment] = []
        self.name = None


    def add(self,segment):
        self.segments.append(segment)
        segment.wire = self

    def moveText(self):
        pass

    def isConnected(self, other):
        ret = False
        for segment in self.getSegments():
            for other_segment in other.getSegments():
                if segment.isConnected(other_segment):
                    ret = True
        return ret

    def getSegments(self):
        return self.segments

    def collidesWithItem(self, item):
        return any(line.collidesWithItem(item) for line in self.getSegments())

    def remove(self, segment):
        self.segments.remove(segment)
        if len(self.getSegments()) == 0:
            self.parent.wireList.remove(self)

    def getPins(self):
        pins = set()
        for segment in self.getSegments():
            pins.update(segment.getPins())
        return pins

    def __setAutoName(self):
        pins = self.getPins()
        symbPins = [p for p in pins if isinstance(p, SymbolPin)]
        designPins = [p for p in pins if isinstance(p, Pin)]

        if len(pins) == 0:
            nextNetIndex = self.parent.getNextNetIndex()
            netName = 'net{}'.format(nextNetIndex)

        elif len(symbPins) > 0:
            pin = symbPins[0]
            netName = pin.getConn()
            for pIdx in range(len(designPins)):
                designPins[pIdx].updName(netName)

        elif len(designPins) > 0:
            # parent type: Design
            nextNetIndex = self.parent.getNextNetIndex()
            netName = 'net{}'.format(nextNetIndex)
            designPins[0].updName(netName)

        self.setName(netName)

    def __setAutoName_bak(self):
        pins = self.getPins()
        if len(pins) == 0:
            nextNetIndex = self.parent.getNextNetIndex()
            netName = 'net{}'.format(nextNetIndex)
        else:
            designPins = [p for p in pins if isinstance(p, Pin)]
            if len(designPins) == 0:
                pin = list(pins)[0]
                netName = pin.getConn()
            else:
                pin = [p for p in pins if not isinstance(p, Pin)][0]
                netName = pin.getConn()
                designPins[0].updName(netName)
        self.setName(netName)

    def getName(self):
        return self.name

    def setName(self,name):
        self.name = name
        self.__updatePinsConn()
        self.__updateSegmentText()

    def __updatePinsConn(self):
        for pin in self.getPins():
            pin.getParent().conns[pin.name] = self.getName()

    def __updateSegmentText(self):
        for segment in self.getSegments():
            segment.text.setPlainText(self.name)

    def complete(self):
        self.__checkParent() # in scene or editing_design
        self.__setAutoName()
        self.__setSelectable()

    def __setSelectable(self):
        for seg in self.getSegments():
            seg.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def __checkParent(self):
        scene = self.parent
        try:
            if scene.editDesign is not None:
                if all(seg.collidesWithItem(scene.editDesign.rect) for seg in self.getSegments()):
                    self.parent = scene.editDesign
                    self.parent.wireList.append(self)
                else:
                    if any(seg.collidesWithItem(scene.editDesign.rect) for seg in self.getSegments()):
                        #TODO: forbidden, alert
                        pass
                    else:
                        scene.wireList.append(self)
            else:
                scene.wireList.append(self)
        except:
            scene.wireList.append(self)

    def toPrevJSON(self, centerX, centerY):
        d = {}
        d['name'] = self.name
        d['segs'] = []
        for seg in self.getSegments():
            d['segs'].append(seg.toPrevJSON(centerX, centerY))

        return d
    def make_by_JSON(self,jsn):
        self.name = jsn['name']
        for seg in jsn['segs']:
            segment = WireSegment()
            segment.make_by_JSON(seg)
            self.add(segment)


class WireList():
    def __init__(self,parent):
        self.wirelist: list[Wire] = []
        #parent is the main scene or a design
        self.parent = parent

    def __iter__(self):
        return self.wirelist.__iter__()

    def __next__(self):
        return self.wirelist.__next__()
    def append(self,new,check=True):
        if check:
            wires_connected = []
            others=[]
            for wire in self.wirelist:
                if new.isConnected(wire):
                    wires_connected.append(wire)
                else:
                    others.append(wire)

            if len(wires_connected)> 0:
                name = wires_connected[0].getName()
                merged = Wire(self.parent)

                for wire in wires_connected + [new]:
                    for segment in wire.getSegments():
                        merged.add(segment)

                merged.setName(name)

                self.wirelist = others + [merged]
            else:
                self.wirelist.append(new)
        else:
            self.wirelist.append(new)
    def cleanup(self):
        for wire in self.wirelist:
            for seg in wire.getSegments():
                seg.scene().removeItem(seg)


    def remove(self,wire, check=True):
        self.wirelist.remove(wire)

    def checkConnectivity(self,wire):
        pass