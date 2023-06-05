from PySide6.QtCore import (Qt, QPointF, QRectF)
from PySide6.QtGui import (QPolygonF, QPen, QColor)
from PySide6.QtWidgets import (
    QGraphicsScene, QInputDialog, QLineEdit, QGraphicsTextItem
)

from src.hmi.text import ParameterText
from src.hmi.line import Line
from src.hmi.rect import Rect
from src.hmi.polygon import Polygon
from src.hmi.ellipse import Circle


class SchScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(QRectF(0, 0, 500, 500))

        self.enableDel = False                  # delete mode
        self.cursorSymb = None                  # list of symbols under cursor
        self.insertSymbType = None              # type of component to insert
        self.widgetMouseMove = None             # widget with moving mouse
        self.designTextLines = None             # list of strings: user-defined design in rectangle
        self.symbols = []                       # list of all symbols, a symbol = list of shapes
        self.wireStartPos = None                # starting point for adding wire
        self.rectStartPos = None                # starting point for adding design rect
        self.rectDesign = None                  # rectangle surrounding the design
        self.scale = 5.0                        # scaling coefficient

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.cleanCursorSymb()
        elif event.key() == Qt.Key_Delete:
            self.delSymb()

    def delSymb(self):
        self.cleanCursorSymb()
        for shape in self.selectedItems():
            shapeInSymb = False
            for symb in self.symbols:
                if shape in symb:
                    shapeInSymb = True
                    for shp in symb:
                        self.removeItem(shp)
            if not shapeInSymb:
                self.removeItem(shape)
    
    def mousePressEvent(self, event):
        if self.enableDel:
            pass
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
            elif self.insertSymbType == 'W':
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
            elif self.insertSymbType == 'W':
                self.drawWire(event, mode='move')
            elif self.insertSymbType == 'RECT':
                self.drawRect(event, mode='move')
            elif self.insertSymbType == 'Design':
                self.drawDesign(event)
            elif self.insertSymbType == 'S':
                self.drawSim(event)
        else:
            for item in self.cursorSymb:
                posx = event.scenePos().x()
                posy = event.scenePos().y()
                if isinstance(item, ParameterText):
                    posx += float(item.posx)
                    posy += float(item.posy)
                item.setPos(posx, posy)

        return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.insertSymbType == 'W':
            self.wireStartPos = None

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
                item = Rect(*ps)
                pen = QPen()
                pen.setWidth(8)
                pen.setColor('green')
                item.setPen(pen)

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

    def drawRes(self, event):
        self.cursorSymb = []
        lines = [[0.000000,375.000000,0.000000,300.000000], 
                 [0.000000,300.000000,-62.500000,281.250000], 
                 [-62.500000,281.250000,62.500000,243.750000], 
                 [62.500000,243.750000,-62.500000,206.250000],
                 [-62.500000,206.250000,62.500000,168.750000], 
                 [62.500000,168.750000,-62.500000,131.250000], 
                 [-62.500000,131.250000,62.500000,93.750000], 
                 [62.500000,93.750000,0.000000,75.000000], 
                 [0.000000,75.000000,0.000000,0.000000]]
        for line in lines:
            line = [l/self.scale for l in line]
            line = Line(*line)
            self.addItem(line)
            self.cursorSymb.append(line)
            line.setPos(event.scenePos())
        pin1 = Rect(0-20/self.scale, 375/self.scale,40/self.scale,40/self.scale)
        self.addItem(pin1)
        self.cursorSymb.append(pin1)
        pin1.setPos(event.scenePos())
        pin2 = Rect(0-20/self.scale, 0-40/self.scale,40/self.scale,40/self.scale)
        self.addItem(pin2)
        self.cursorSymb.append(pin2)
        pin2.setPos(event.scenePos())

        name = ParameterText('    R1\n\n    R')
        self.addItem(name)
        self.cursorSymb.append(name)
        name.setPos(event.scenePos())


        self.symbols.append(self.cursorSymb)


    def drawGnd(self, event):
        self.cursorSymb = []
        points=[[-62.500000,187.500000], [62.500000,187.500000], [0.000000,250.000000]]
        polygonf = QPolygonF()
        for point in points:
            polygonf.append(QPointF(point[0]/self.scale,point[1]/self.scale))
        ground = Polygon(polygonf)
        self.addItem(ground)
        self.cursorSymb.append(ground)
        ground.setPos(event.scenePos())

        line = [0.000000,0.000000,0.000000,187.500000]
        line = [l/self.scale for l in line]
        line = Line(*line)
        self.addItem(line)
        self.cursorSymb.append(line)
        line.setPos(event.scenePos())

        pin=Rect(0-20/self.scale, 0-40/self.scale,40/self.scale,40/self.scale)
        self.addItem(pin)
        self.cursorSymb.append(pin)
        pin.setPos(event.scenePos())
        self.symbols.append(self.cursorSymb)

    def drawVsrc(self, event):
        self.cursorSymb = []
        lines = [[0.000000,175.000000,0.000000,137.500000],
                 [18.750000,156.250000,-18.750000,156.250000],
                 [0.000000,125.000000,0.000000,0.000000],
                 [0.000000,250.000000,0.000000,375.000000],
                 [18.750000,218.750000,-18.750000,218.750000]]
        for line in lines:
            line = [l/self.scale for l in line]
            line = Line(*line)
            self.addItem(line)
            self.cursorSymb.append(line)
            line.setPos(event.scenePos())
        cp = [p/self.scale for p in [0.000000,187.500000,68.750000]]
        circle = Circle(cp[0]-cp[2], cp[1]-cp[2], cp[2]*2,cp[2]*2)
        self.addItem(circle)
        self.cursorSymb.append(circle)
        circle.setPos(event.scenePos())

        pin1 = Rect(0-20/self.scale, 375/self.scale,40/self.scale,40/self.scale)
        self.addItem(pin1)
        self.cursorSymb.append(pin1)
        pin1.setPos(event.scenePos())
        pin2 = Rect(0-20/self.scale, 0-40/self.scale,40/self.scale,40/self.scale)
        self.addItem(pin2)
        self.cursorSymb.append(pin2)
        pin2.setPos(event.scenePos())

        name = ParameterText('    V1\n\n    V')
        self.addItem(name)
        self.cursorSymb.append(name)
        name.setPos(event.scenePos())

        self.symbols.append(self.cursorSymb)

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
            polygonf.append(QPointF(point[0]/self.scale, point[1]/self.scale))
        iopin = Polygon(polygonf)
        iopin.setPen(QPen('red'))
        iopin.setBrush(QColor('red'))
        self.addItem(iopin)
        self.cursorSymb.append(iopin)
        iopin.setPos(event.scenePos())

        self.symbols.append(self.cursorSymb)

    def cleanCursorSymb(self):
        if self.cursorSymb is not None:
            for shape in self.cursorSymb:
                self.removeItem(shape)
            self.cursorSymb=None
        self.insertSymbType = 'NA'
        self.wireStartPos = None
        self.rectStartPos = None

    def drawWire(self, event, mode=None):
        # mode: 'press', 'move'
        curPos = event.scenePos()
        curX, curY = curPos.x(), curPos.y()

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
        line = Line(*line)
        line.setPen(QColor('blue'))
        self.addItem(line)

        if mode == 'move':
            self.widgetMouseMove = line
        else:
            self.wireStartPos = endPos
            self.widgetMouseMove = None

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
        rect = Rect(startX, startY, width, height)
        pen = QPen()
        pen.setWidth(8)
        pen.setColor('green')
        rect.setPen(pen)
        self.addItem(rect)

        if mode == 'move' :
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
        font.setPixelSize(50)
        item.setFont(font)
        item.setPos(event.scenePos())
        self.addItem(item)
        self.cursorSymb.append(item)
        self.symbols.append(self.cursorSymb)