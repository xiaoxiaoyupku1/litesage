import re
import json

from PySide6.QtCore import (Qt)
from src.hmi.line import Line, WireList, WireSegment, Wire
from src.hmi.rect import Rect, DesignBorder
from src.hmi.polygon import Polygon, Pin
from src.hmi.ellipse import Circle
from src.hmi.text import ParameterText
from src.hmi.group import SchInst


class Design:
    def __init__(self, scene, rect=None):
        self.model = 'MODEL1'
        self.name = 'X1'
        self.pins = []  # pin names
        self.conns = {}  # pin name -> wire name
        self.initial_conns = {}

        # design status
        self.readonly = False

        # items linked to design
        self.scene = scene
        self.symbols = []
        self.wireList = WireList(self)
        self.rect = rect
        self.Pins = []  # Pins

        if rect is not None:
            self.make_by_rect()

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
        for wire in wires:
            self.wireList.append(wire,check=False)
            self.scene.wireList.remove(wire, check=False)

    def make_by_lines(self, lines):
        jsn = json.loads(lines[0].split(':', maxsplit=1)[1])
        for k in ['model', 'pins', 'conns']:
            setattr(self, k, jsn[k])
        self.initial_conns = self.conns.copy()

        jsn = json.loads(lines[1].split(':', maxsplit=1)[1])
        rect = DesignBorder(*jsn)
        self.rect = rect
        self.change_to_readonly()
        self.rect.design = self

        jsn = json.loads(lines[3].split(':', maxsplit=1)[1])
        for p in jsn:
            pn = Pin()
            pn.make_by_JSON(p, self.scene)
            pn.setDesign(self)
            self.Pins.append(pn)

        for sym_line in lines[4:]:
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
        while 'Pin' + str(name_id) in self.pins:
            name_id += 1
        Pin.name = 'Pin' + str(name_id)
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

            # part 4: Pins
            f.write('Pins:')
            pins=[]
            for pin in self.Pins:
                pins.append(pin.toPrevJSON(centerX, centerY))
            f.write(json.dumps(pins))
            f.write("\n")

            #part 5: symbols
            scale = self.scene.scale
            for symbol in self.symbols:
                f.write('Symbol:')
                sym = symbol.toPrevJSON(centerX,centerY)
                f.write(json.dumps(sym))
                f.write("\n")
