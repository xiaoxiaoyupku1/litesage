import json
import os

from PySide6.QtCore import (Qt)
from src.hmi.line import WireList, WireSegment, Wire
from src.hmi.rect import Rect, DesignBorder, SymbolPin
from src.hmi.polygon import Polygon, Pin
from src.hmi.ellipse import Circle
from src.hmi.text import ParameterText, DesignInfo
from src.hmi.group import (SchInst, DesignGroup)
from src.hmi.ellipse import WireConnection
from PySide6.QtWidgets import (QGraphicsItemGroup, QGraphicsItem)
from src.tool.sys import readFile


class Design:
    def __init__(self, scene, rect=None):
        self.model = 'MODEL1'
        self.name = 'X1'
        self.pins = []  # pin names
        self.conns = {}  # pin name -> wire name
        self.initial_conns = {}

        self.group: QGraphicsItemGroup = None
        self.show = Qt.Checked

        # design status
        self.readonly = False

        # items linked to design
        self.scene = scene
        self.symbols = []
        self.wireList = WireList(self)
        self.rect = rect
        self.Pins = []  # Pins
        self.connections = set() # wire connections
        self.info = DesignInfo(design=self) #

        if rect is not None:
            self.make_by_rect()

    def updateInfo(self):
        self.info.setPlainText(self.model+'\n'+self.name)


    def change_to_editable(self):
        self.readonly = False
        self.rect.pen.setStyle(Qt.DotLine)

    def change_to_readonly(self):
        self.readonly = True
        self.rect.pen.setStyle(Qt.SolidLine)
        self.rect.setPen(self.rect.pen)

    def make_by_rect(self):
        self.rect.design = self
        wires = set()
        for item in self.rect.collidingItems():
            if type(item) is SchInst:
                self.symbols.append(item)
                self.scene.symbols.remove(item)
            elif type(item) is WireSegment:
                wires.add(item.wire)
            elif type(item) is WireConnection:
                self.connections.add(item)
        for wire in wires:
            self.wireList.append(wire,check=False)
            self.scene.wireList.remove(wire, check=False)

    def make_by_lines(self, lines, nextNetIndex):
        jsn = json.loads(lines[0].split(':', maxsplit=1)[1])
        for k in ['model', 'pins', 'conns']:
            setattr(self, k, jsn[k])
        self.initial_conns = self.conns.copy()
        for pinIdx, pin in enumerate(self.pins):
            self.conns[pin] = 'net{}'.format(nextNetIndex + pinIdx)

        jsn = json.loads(lines[1].split(':', maxsplit=1)[1])
        rect = DesignBorder(*jsn)
        self.rect = rect
        self.change_to_readonly()
        self.rect.design = self

        jsn = json.loads(lines[4].split(':', maxsplit=1)[1])
        for idx, p in enumerate(jsn):
            pn = Pin()
            pn.name = self.pins[idx]
            pn.make_by_JSON(p, self.scene)
            pn.setDesign(self)
            self.Pins.append(pn)

        for sym_line in lines[5:]:
            jsn = json.loads(sym_line.split(':', maxsplit=1)[1])
            symbol = SchInst()
            symbol.make_by_JSON(jsn, self.scene)
            self.symbols.append(symbol)

        jsn = json.loads(lines[2].split(':', maxsplit=1)[1])
        self.wireList = WireList(self)
        for wr in jsn:
            wire = Wire(self)
            wire.make_by_JSON(wr)
            self.wireList.append(wire, check=False)

        jsn = json.loads(lines[3].split(':', maxsplit=1)[1])
        for cnn in jsn:
            conn = WireConnection()
            conn.make_by_JSON(cnn)
            self.connections.add(conn)

        self.updateInfo()
        self.info.setPosInDesign()

    def delete(self):
        if self.readonly:
            self.wireList.cleanup()
            self.wireList = None
            for symbol in self.symbols:
                self.scene.removeItem(symbol)
            self.scene.removeItem(self.rect)
            for pin in self.Pins:
                self.scene.removeItem(pin)
            self.scene.designs.remove(self)
        else:
            for wire in self.wireList:
                self.scene.wireList.append(wire, check=False)
            self.wireList = None
            for symbol in self.symbols:
                self.scene.symbols.append(symbol)
            self.symbols = []
            self.scene.removeItem(self.rect)
            self.pins = []
            self.conns = {}
            for Pin in self.Pins:
                self.scene.removeItem(Pin)
            self.Pins = []
            self.scene.editDesign = None

    def addPin(self, Pin):
        name_id = 1
        while 'pin' + str(name_id) in self.pins:
            name_id += 1
        Pin.name = 'pin' + str(name_id)
        self.pins.append(Pin.name)
        self.Pins.append(Pin)
        self.conns[Pin.name] = 'node'+str(name_id)
        self.initial_conns = self.conns.copy()

    def delPin(self, Pin):
        self.pins.remove(Pin.name)
        self.conns.pop(Pin.name)
        self.initial_conns = self.conns.copy()
        self.Pins.remove(Pin)

    def dumpDesign(self, filePath):
        rect = self.rect.rect()
        rectW = rect.width()
        rectH = rect.height()
        rectX = rect.x()
        rectY = rect.y()
        centerX = rectX + rectW / 2
        centerY = rectY + rectH / 2

        with open(filePath, 'w') as f:
            #first row: UNKNOWN_MODEL,node1,net2 ...
            f.write('MODEL:')
            f.write(json.dumps({'model':self.model,'pins':self.pins,'conns':self.conns}))
            f.write("\n")

            # 2nd row: rect of design
            f.write('RECT:')
            items = [rectX - centerX, rectY - centerY, rectW, rectH]
            f.write(json.dumps(items))
            f.write('\n')

            # part 3: wires
            f.write('Wires:')
            wires = []
            for wire in self.wireList.wirelist:
                wires.append(wire.toPrevJSON(centerX, centerY))
            f.write(json.dumps(wires))
            f.write('\n')

            #part 4: connections of wires
            f.write('Connections:')
            conns = set()
            for wire in self.wireList.wirelist:
                for seg in wire.getSegments():
                    conns.update(seg.connections)
            conns_list=[]
            for conn in conns:
                conns_list.append(conn.toPrevJSON(centerX, centerY))
            f.write(json.dumps(conns_list))
            f.write('\n')


            # part 5: Pins
            f.write('Pins:')
            pins=[]
            for pin in self.Pins:
                pins.append(pin.toPrevJSON(centerX, centerY))
            f.write(json.dumps(pins))
            f.write("\n")

            #part 6: symbols
            scale = self.scene.scale
            for symbol in self.symbols:
                f.write('Symbol:')
                sym = symbol.toPrevJSON(centerX,centerY)
                f.write(json.dumps(sym))
                f.write("\n")

    def setScale(self, scale: float):
        self.group.setScale(scale)

    def make_group(self):
        if self.group is None:
            self.group = DesignGroup()
            self.group.setDesign(self)
            self.scene.addItem(self.group)

            for sym in self.symbols:
                self.group.addToGroup(sym)

            self.group.addToGroup(self.rect)

            for wire in self.wireList.wirelist:
                for seg in wire.getSegments():
                    self.group.addToGroup(seg)

            for pn in self.Pins:
                self.group.addToGroup(pn)

            for conn in self.connections:
                self.group.addToGroup(conn)

            self.group.addToGroup(self.info)



    def setShow(self, show):
        self.show = show
        if self.show == Qt.Unchecked:
            for sym in self.symbols:
                sym.setOpacity(0)


            for wire in self.wireList.wirelist:
                for seg in wire.getSegments():
                    seg.setOpacity(0)

            for conn in self.connections:
                conn.setOpacity(0)

            self.info.setOpacity(1)

        elif self.show == Qt.Checked:
            for sym in self.symbols:
                if type(sym) is SymbolPin:
                    if sym.status is False:
                        sym.setOpacity(1)
                    else:
                        pass
                else:
                    sym.setOpacity(1)

            for wire in self.wireList.wirelist:
                for seg in wire.getSegments():
                    seg.setOpacity(1)

            for conn in self.connections:
                conn.setOpacity(1)

            self.info.setOpacity(0)


    @classmethod
    def loadAllDesigns(cls, directory='./project/'): # -> dict[str, list]:
        designSymbols = {}
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        for file in os.listdir(directory):
            if file.endswith('.dsgn'):
                filePath = os.path.join(directory, file)
                lines = [line for line in readFile(filePath)]
                model = json.loads(lines[0].split(':', maxsplit=1)[1])['model']
                designSymbols[model] = lines
        return designSymbols