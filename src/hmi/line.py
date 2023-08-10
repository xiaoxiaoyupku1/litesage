from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsItem)
from PySide6.QtCore import Qt,QLineF
from PySide6.QtWidgets import ( QGraphicsScene )

from src.hmi.dialog import WireDialog
from src.hmi.text import WireNameText
from src.hmi.rect import  SymbolPin
from src.hmi.polygon import Pin


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
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
    def addPin(self,pin):
        self.pins.add(pin)
    def removePin(self,pin):
        self.pins.remove(pin)
    def getPins(self):
        return self.pins
    def addPins(self):
        for item in self.collidingItems():
            if type(item) is SymbolPin or type(item) is Pin:
                self.addPin(item)
                item.setConnected()


    def contextMenuEvent(self, event):
        dialog = WireDialog(parent=None, wiresegment=self)
        if dialog.exec():
            netName = dialog.name.text().strip()
            self.wire.setName(netName)
            for designPin in [p for p in self.getPins() if isinstance(p, Pin)]:
                designPin.updName(netName)

            if self.text not in self.scene().items():
                self.scene().addItem(self.text)
            self.text.setPos(event.pos())

    def delete(self):
        for pin in self.getPins():
            pin.setDisConnected()
            pin.getParent().conns[pin.name] = pin.getParent().initial_conns[pin.name]
        self.scene().removeItem(self.text)
        self.scene().removeItem(self)
        self.wire.remove(self)
        self.wire.parent.wireList.checkConnectivity(self.wire)

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
    def toPrevJSON(self, centerX, centerY):
        line = self.line()
        items = [line.x1() - centerX, line.y1() - centerY, line.x2() - centerX, line.y2() - centerY]
        return items
    def make_by_JSON(self,jsn):
        self.setLine(QLineF(*jsn))

class Wire(): # Wire is a list of WireSegment
    def __init__(self,parent):
        self.parent = parent #scene or design
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
            self.parent.wireList.remove(self)

    def getPins(self):
        pins = set()
        for segment in self.getSegments():
            pins.update(segment.getPins())
        return pins

    def __setAutoName(self):
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
            #print(pin)
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
        self.wirelist=[]
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