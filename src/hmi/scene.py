from PySide6.QtCore import (Qt, QPointF)
from PySide6.QtGui import (QPolygonF, QPen, QColor)
from PySide6.QtWidgets import (
    QGraphicsScene, QInputDialog, QLineEdit, QGraphicsTextItem,
)

from src.hmi.text import ParameterText
from src.hmi.dialog import NetlistDialog
from src.hmi.line import Line, Wire, WireSegment, WireList
from src.hmi.rect import Rect, DesignBorder, SymbolPin
from src.hmi.polygon import Polygon
from src.hmi.ellipse import Circle
from src.hmi.symbol import Symbol
from src.hmi.group import SchInst
from src.tool.device import getDeviceInfos
from src.tool.netlist import createNetlist


class SchScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

        self.enableDel = False  # delete mode
        self.cursorSymb = None  # group of items under cursor
        self.insertSymbType = None  # type of component to insert
        self.insertSymbName = None  # insert symbol name (from lib file)
        self.widgetMouseMove = None  # widget with moving mouse
        self.designTextLines = None  # list of strings: user-defined design in rectangle
        self.symbols = []  # list of all symbols, a symbol = list of shapes

        self.wireStartPos = None  # starting point for adding wire
        self.wireList = WireList(self)
        self.currentWire = Wire(self)

        self.rectStartPos = None  # starting point for adding design rect
        self.rectDesign = None  # rectangle surrounding the design
        self.scale = 15.0  # scaling coefficient
        self.sceneSymbRatio = 125 / self.scale  # x / 50 = 62.5 * 2 / 750
        self.gridOn = True  # flag grid
        self.gridPen = None
        self.isThumbnail = False

        self.basicSymbols = None  # basic ideal symbols
        self.basicDevInfo = None
        self.initBasicDevices()
        self.pdkSymbols = None  # pdk symbols
        self.pdkDevInfo = None
        self.ipSymbols = None  # ip symbols
        self.ipDevInfo = None

    def initBasicDevices(self):
        if self.basicSymbols is None or self.basicDevInfo is None:
            self.basicSymbols = Symbol.parser(r'devicelib\basic.lib')
            self.basicDevInfo = getDeviceInfos(r'devicelib\basic.info')

    def initPdkDevices(self):
        if self.pdkSymbols is None or self.pdkDevInfo is None:
            self.pdkSymbols = Symbol.parser(r'devicelib\pdk.lib')
            self.pdkDevInfo = getDeviceInfos(r'devicelib\pdk.info')

    def initIpDevices(self):
        if self.ipSymbols is None or self.ipDevInfo is None:
            self.ipSymbols = {}
            # self.ipSymbols = Symbol.parser(r'devicelib\ip.lib')
            self.ipDevInfo = {}
            # self;ipDevInfo = DeviceInfo.parser(r'devicelib\ip.lib')

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.endWire()
            self.cleanCursorSymb()
        elif event.key() == Qt.Key_Delete:
            self.delSymb()

    def delSymb(self):
        self.cleanCursorSymb()
        for shape in self.selectedItems():
            if type(shape) is WireSegment:
                shape.delete()
            elif type(shape) is SchInst:
                pins = [item for item in shape.childItems() if type(item) is SymbolPin]
                for pin in pins:
                    wiresegments = [ item for item in pin.collidingItems() if type(item) is WireSegment]
                    for wiresegment in wiresegments:
                        wiresegment.removePin(pin)
                if shape in self.symbols:  # wire is not included
                    self.symbols.remove(shape)
                self.removeItem(shape)
            else:
                #not wire or symbol
                self.removeItem(shape)


    def roundPos(self, origX, origY):
        posx1 = int(origX / self.sceneSymbRatio) * self.sceneSymbRatio
        posx2 = posx1 + self.sceneSymbRatio
        posx3 = posx1 - self.sceneSymbRatio

        posy1 = int(origY / self.sceneSymbRatio) * self.sceneSymbRatio
        posy2 = posy1 + self.sceneSymbRatio
        posy3 = posy1 - self.sceneSymbRatio

        minDist = None
        for posxi in (posx1, posx2, posx3):
            for posyi in (posy1, posy2, posy3):
                dist = (origX - posxi) ** 2 + (origY - posyi) ** 2
                if minDist is None or dist < minDist:
                    minDist = dist
                    posx, posy = posxi, posyi

        return posx, posy

    def mousePressEvent(self, event):
        if self.enableDel:
            pass
        else:
            if self.insertSymbType in ['basic', 'pdk', 'ip']:
                self.wireStartPos = None
                self.drawSymbol(event, self.insertSymbName, self.insertSymbType)
            else:
                if self.insertSymbType == 'R':
                    self.wireStartPos = None
                    self.drawRes(event)
                elif self.insertSymbType == 'G':
                    self.wireStartPos = None
                    self.drawGnd(event)
                elif self.insertSymbType == 'V':
                    self.wireStartPos = None
                    self.drawVsrc(event)
                if self.insertSymbType == 'W':
                    self.drawWire(event)
                elif self.insertSymbType == 'P':
                    self.drawPin(event)
                elif self.insertSymbType == 'RECT':
                    self.drawRect(event)
                elif self.insertSymbType == 'Design':
                    self.drawDesign(event)
                elif self.insertSymbType == 'S':
                    self.drawSim(event)
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.cursorSymb is None:
            if self.insertSymbType == 'R':
                self.drawRes(event)
            elif self.insertSymbType == 'G':
                self.drawGnd(event)
            elif self.insertSymbType == 'V':
                self.drawVsrc(event)
            elif self.insertSymbType == 'P':
                self.drawPin(event)
            elif self.insertSymbType in ['basic', 'pdk', 'ip']:
                self.drawSymbol(event, self.insertSymbName, self.insertSymbType)
            elif self.insertSymbType == 'W':
                self.drawWire(event, mode='move')
            elif self.insertSymbType == 'RECT':
                self.drawRect(event, mode='move')
            elif self.insertSymbType == 'Design':
                self.drawDesign(event)
            elif self.insertSymbType == 'S':
                self.drawSim(event)
        else:
            posx, posy = self.roundPos(event.scenePos().x(), event.scenePos().y())
            self.cursorSymb.setPos(posx, posy)

        return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.endWire()
    def endWire(self):
        if self.insertSymbType == 'W':
            self.wireStartPos = None
            self.currentWire.complete()
            self.wireList.append(self.currentWire)
            self.currentWire = Wire(self)

    def drawDesign(self, event):
        self.cursorSymb = []
        for itemDef in self.designTextLines:
            itemDef = itemDef.rstrip()
            name, parameters = itemDef.split(':')

            if name == 'Line':
                ps = [float(p) for p in parameters.split(',')]
                item = Line(*ps)

            elif name == 'Rect':
                ps = [float(p) for p in parameters.split(',')]
                item = Rect(*ps)

            elif name == 'Polygon' or name == "Pin":
                points = parameters.split(';')
                polygonf = QPolygonF()
                for point in points:
                    point_array = [float(i) for i in point.split(',')]
                    polygonf.append(QPointF(*point_array))
                item = Polygon(polygonf)
                if name == "Pin":
                    item.setPen(QPen('red'))
                    item.setBrush(QColor('red'))

            elif name == 'Circle':
                ps = [float(p) for p in parameters.split(',')]
                item = Circle(*ps)

            elif name == 'RECT':
                ps = [float(p) for p in parameters.split(',')]
                item = DesignBorder(*ps)

            elif name == 'Wire':
                ps = [float(p) for p in parameters.split(',')]
                item = Line(*ps)
                item.setPen(QColor('blue'))

            elif name == 'Parameter':
                n, v, x, y = parameters.split(',')
                item = ParameterText('    ' + n + '\n\n    ' + v)
                item.posx = x
                item.posy = y

            self.addItem(item)
            self.cursorSymb.append(item)

            posx = event.scenePos().x()
            posy = event.scenePos().y()
            if isinstance(item, ParameterText):
                posx += float(item.posx)
                posy += float(item.posy)
            item.setPos(posx, posy)

        self.symbols.append(self.cursorSymb)

    def drawSymbol(self, event, name, symbType='basic'):
        if symbType == 'basic':
            symbols = self.basicSymbols
            devinfo = self.basicDevInfo
        elif symbType == 'pdk':
            symbols = self.pdkSymbols
            devinfo = self.pdkDevInfo
        else:
            assert 0, 'ip symbols not implemented yet'
            symbols = self.ipSymbols
        self.cursorSymb = []

        inst = SchInst()
        shapes = symbols[name].parts
        inst.draw(self, name, shapes, devinfo, self.isThumbnail)

        self.addItem(inst)
        if isinstance(event, list):
            inst.setPos(*event)
        else:
            inst.setPos(event.scenePos())
        self.cursorSymb = inst
        self.symbols.append(self.cursorSymb)

    def drawRes(self, event):
        self.drawSymbol(event, 'RES', 'basic')

    def drawVsrc(self, event):
        self.drawSymbol(event, 'VSRC', 'basic')

    def drawPin(self, event):
        self.cursorSymb = []
        points = [[87.500000, 0.000000],
                  [31.250000, 56.250000],
                  [-31.250000, 56.250000],
                  [-87.500000, 0.000000],
                  [-31.250000, -56.250000],
                  [31.250000, -56.250000]]
        polygonf = QPolygonF()
        for point in points:
            polygonf.append(QPointF(point[0] / self.scale, point[1] / self.scale))
        iopin = Polygon(polygonf)
        iopin.setPen(QPen('red'))
        iopin.setBrush(QColor('red'))
        self.addItem(iopin)
        self.cursorSymb.append(iopin)
        iopin.setPos(event.scenePos())

        self.symbols.append(self.cursorSymb)

    def cleanCursorSymb(self):
        if self.cursorSymb is not None:
            self.removeItem(self.cursorSymb)
            self.symbols.remove(self.cursorSymb)
            self.cursorSymb = None
        self.insertSymbType = 'NA'
        self.wireStartPos = None
        self.rectStartPos = None

    def drawWire(self, event, mode=None):
        # mode: 'press', 'move'
        curPos = event.scenePos()
        curX, curY = self.roundPos(curPos.x(), curPos.y())

        if self.widgetMouseMove is not None:
            self.removeItem(self.widgetMouseMove)

        if self.wireStartPos is None:
            if mode != 'move':
                self.wireStartPos = [curX, curY]
            return

        diffX = abs(curX - self.wireStartPos[0])
        diffY = abs(curY - self.wireStartPos[1])
        if diffX <= diffY:
            endPos = [self.wireStartPos[0], curY]
        else:
            endPos = [curX, self.wireStartPos[1]]
        line = self.wireStartPos + endPos
        wireseg = WireSegment(*line)
        self.addItem(wireseg)

        if mode == 'move':
            self.widgetMouseMove = wireseg
        else:
            self.wireStartPos = endPos
            self.widgetMouseMove = None
            wireseg.addPins()
            self.currentWire.add(wireseg)

    def drawRect(self, event, mode=None):
        # mode: 'press', 'move'
        curPos = event.scenePos()
        curX, curY = curPos.x(), curPos.y()

        if self.widgetMouseMove is not None:
            self.removeItem(self.widgetMouseMove)

        if self.rectStartPos is None:
            if mode != 'move':
                self.rectStartPos = [curX, curY]
            return

        # leftTop is (0, 0)
        width = abs(curX - self.rectStartPos[0])
        height = abs(curY - self.rectStartPos[1])
        startX = min(curX, self.rectStartPos[0])
        startY = min(curY, self.rectStartPos[1])
        rect = DesignBorder(startX, startY, width, height)
        self.addItem(rect)

        if mode == 'move':
            self.widgetMouseMove = rect
        else:
            self.rectStartPos = None
            self.rectDesign = rect
            self.widgetMouseMove = None

    def drawSim(self, event):
        self.cursorSymb = []
        text, ok = QInputDialog.getText(None,
                                        'SPICE Analysis',
                                        'Simulation command:',
                                        QLineEdit.Normal,
                                        '.dc temp -5 50 1')
        if not ok or len(text.strip()) == 0:
            return
        item = QGraphicsTextItem(text)
        item.setDefaultTextColor('darkblue')
        font = item.font()
        font.setPixelSize(25)
        item.setFont(font)
        item.setPos(event.scenePos())
        self.addItem(item)
        self.cursorSymb.append(item)
        self.symbols.append(self.cursorSymb)

    def drawBackground(self, painter, rect):
        if self.gridPen is None:
            pen = QPen()
            pen.setCapStyle(Qt.RoundCap)
            pen.setColor('lightgray')
            self.gridPen = pen

        if self.gridOn:
            painter.setPen(self.gridPen)
            ratio = self.sceneSymbRatio * 3
            startX = int(rect.x() / ratio) - 1
            startY = int(rect.y() / ratio) - 1
            endX = int(rect.right() / ratio) + 1
            endY = int(rect.bottom() / ratio) + 1
            for posx in range(startX, endX, 1):
                posx *= ratio
                for posy in range(startY, endY, 1):
                    posy *= ratio
                    painter.drawPoint(posx, posy)

    def toggleGrid(self):
        self.gridOn = not self.gridOn
        self.update()

    def showNetlist(self):
        netlist = createNetlist(self)
        dialog = NetlistDialog(None, netlist)
        dialog.exec()

    def clear(self):
        self.symbols = []
        super().clear()

'''
    def hidePins(self):
        for sym in self.symbols:
            pins = [ shape for shape in sym.childItems() if type(shape) is SymbolPin]
            for pin in pins:
                for wire in self.wireList:
                    if wire.collidesWithItem(pin):
                        pin.hide()
                        break

'''