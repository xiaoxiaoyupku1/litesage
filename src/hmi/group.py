from PySide6.QtWidgets import (QGraphicsItemGroup, QGraphicsItem)
from PySide6.QtCore import (Qt, QPointF)
from PySide6.QtGui import (QPolygonF, QPen, QColor)

from src.hmi.dialog import ParameterDialog
from src.hmi.text import Text, ParameterText
from src.hmi.line import Line, Bus
from src.hmi.rect import SymbolPin
from src.hmi.polygon import Polygon
from src.hmi.ellipse import Circle, Arc
import re


class SchInst(QGraphicsItemGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.nameHead = None
        self.nameId = None
        self.name = None
        self.model = None
        self.pins = []
        self.conns = {} #pin name -> wire name
        self.paramText = None
        self.params = [] # list of DeviceParam
        self.space = ''

    def paint(self, painter, option, widget=None, *args, **kwargs):
        if self.isSelected():
            pen = QPen()
            pen.setStyle(Qt.DotLine)
            pen.setWidth(pen.width()/2)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def setInstName(self, nameHead, nameId):
        self.nameHead = nameHead
        self.nameId = nameId 

    def isPin(self):
        return self.model == 'PIN'

    def contextMenuEvent(self, event):
        if self.isPin():
            return
        dialog = ParameterDialog(parent=None, 
                                 item=self.paramText, 
                                 params=self.params)
        if dialog.exec():
            self.name = dialog.name.text()
            for idx, value in enumerate(dialog.values):
                self.params[idx].name = value[0]
                self.params[idx].value = value[1].text()
            self.setParamText()

            nameHead = self.name[0].upper()
            nameId = self.name[1:]
            if re.search('^\d+$', nameId):
                nameId = int(nameId)
                self.setInstName(nameHead, nameId)
            else:
                self.setInstName(None, None)

    def draw(self, scene, model, shapes, devinfo, isThumbnail=False):
        nameHead = devinfo[model].head
        params = devinfo[model].getParamList()
        nameId = self.getAutoNameId(scene, nameHead)
        self.setInstName(nameHead, nameId)
        self.name = nameHead + str(nameId)
        self.model = model
        self.pins = devinfo[model].pins
        self.conns = {p:'node{}'.format(idx) for idx, p in enumerate(self.pins)}
        self.initial_conns = self.conns.copy()
        for shape_params in shapes:
            shape = self.draw_shape(scene, shape_params)
            if shape is not None:
                self.addToGroup(shape)

        if isThumbnail:
            return

        self.params = params
        self.paramText = ParameterText()
        if not self.isPin():
            self.setParamText()
        right = self.boundingRect().x() + self.boundingRect().width()
        self.paramText.setPos(right,self.boundingRect().y())
        self.addToGroup(self.paramText)

    def setParamText(self):
        p = [self.space + self.name, self.model]
        for param in self.params:
            name, value = param.getName(), param.getValue()
            if name == '' or name.lower() == 'value':
                p.append(self.space + value)
            else:
                p.append(self.space + name[0]+'='+value)
        text = '\n'.join(p)
        self.paramText.setPlainText(text)

    def getAutoNameId(self, scene, nameHead):
        num_set = set()
        for symbol in scene.symbols:
            if symbol.nameHead is not None:
                if nameHead == symbol.nameHead:
                    if symbol.nameId is not None:
                        num_set.add(symbol.nameId)
        id_num = 1
        while id_num in num_set:
            id_num += 1
        return id_num

    def draw_shape(self, scene, shape_params):
        # shape_params is  a list from lib file to describe a shape
        shape_type = shape_params[0].lower()
        p = None
        if shape_type == 'wire':
            tokens = shape_params[1:]
            tokens = [float(token) / scene.scale for token in tokens]
            p = Line(*tokens)
        elif shape_type == 'bus':
            tokens = shape_params[1:]
            tokens = [float(token) / scene.scale for token in tokens]
            p = Bus(*tokens)
        elif shape_type == 'c':
            tokens = shape_params
            cp = [float(p) / scene.scale for p in tokens[1:4]]
            p = Circle(cp[0] - cp[2], cp[1] - cp[2], cp[2] * 2, cp[2] * 2)
        elif shape_type == 'p':
            polygonf = QPolygonF()
            for i in range(5, len(shape_params) - 1, 2):
                polygonf.append(QPointF(float(shape_params[i]) / scene.scale, float(shape_params[i + 1]) / scene.scale))
            p = Polygon(polygonf)
            if self.isPin():
                p.pen.setColor('red')
                p.setPen(p.pen)
            if shape_params[-1].lower() == 'f':
                p.setBrush(p.pen.color())
        elif shape_type == 'x':
            name = shape_params[1]
            num = shape_params[2]
            pos_x = float(shape_params[3])
            pos_y = float(shape_params[4])
            pin_len = float(shape_params[5])
            orientation = shape_params[6]
            Snum = float(shape_params[7])
            half = Snum / 2
            p = SymbolPin((pos_x - half) / scene.scale, (pos_y - half) / scene.scale,
                          Snum / scene.scale, Snum / scene.scale)
            p.setName(name)
        elif shape_type == 'a':
            pos_x = float(shape_params[1])
            pos_y = float(shape_params[2])
            radius = float(shape_params[3])
            start = float(shape_params[4]) / 10
            end = float(shape_params[5]) / 10
            p = Arc((pos_x - radius) / scene.scale, (pos_y - radius) / scene.scale,
                    radius / scene.scale * 2, radius / scene.scale * 2)
            p.setStartAngle(start * 16)
            p.setSpanAngle((end - start) * 16)
        elif shape_type == 'label':
            pos_x = float(shape_params[1])
            pos_y = float(shape_params[2])
            orient = '0'
            dimension = float(shape_params[4])
            text = shape_params[5]
            p = Text(text=text, posx=pos_x / scene.scale, posy=pos_y / scene.scale,
                     orient=orient, dimension=dimension / scene.scale)
        else:
            pass

        return p
