from PySide6.QtWidgets import (QGraphicsItemGroup, QGraphicsItem)
from PySide6.QtCore import (Qt, QPointF)
from PySide6.QtGui import (QPolygonF, QPen, QColor)

from src.hmi.dialog import ParameterDialog
from src.hmi.text import Text, ParameterText
from src.hmi.line import Line, Bus
from src.hmi.rect import SymbolPin
from src.hmi.polygon import Polygon
from src.hmi.ellipse import Circle, Arc
from src.tool.device import DeviceParam
from src.hmi.dialog import DesignDialog
import re

class SchInst(QGraphicsItemGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.nameHead = None
        self.nameId = None
        self.name = None
        self.lib = None # basic, pdk, ip
        self.model = None
        self.pins = []
        self.conns = {} # pin name -> wire name
        self.initial_conns = {}
        self.paramText = None
        self.params = [] # list of DeviceParam
        self.space = ''
        self.SymbolPins = []

    def toPrevJSON(self, centerX, centerY):
        params =  [p.toPrevJSON() for p in self.params]
        ret = {k: getattr(self, k) for k in ['nameHead',
                                            'nameId',
                                             'name',
                                             'model',
                                             'pins',
                                             'conns',
                                             'initial_conns',
                                             'space',
                                             'lib']}
        ret['scale'] = self.scale()
        ret['rotation'] = self.rotation()
        ret['m11'] = self.transform().m11()
        ret['m22'] = self.transform().m22()

        ret['params'] = params
        distx, disty = [self.x() - centerX, self.y() - centerY]

        ret['distx'] = distx
        ret['disty'] = disty

        ret['pins_status'] = []
        ret['shapes'] = []
        for shape in self.SymbolPins:
            row = ['x', shape.name,'_']
            snum = shape.rect().width() * self.scene().scale
            half = snum / 2
            pos_x =  (shape.rect().x() + distx) * self.scene().scale + half
            pos_y =  (shape.rect().y() + disty) * self.scene().scale + half
            row += [pos_x, pos_y, 0, 0, snum]
            ret['shapes'].append(row)
            if shape.status:
                ret['pins_status'].append(True)
            else:
                ret['pins_status'].append(False)

        text = self.paramText.toPlainText()
        text_x = self.paramText.x() +distx
        text_y = self.paramText.y() +disty
        ret['paramText'] = [text, text_x, text_y]

        for shape in self.childItems():
            if type(shape) is Line:
                row = ['wire']
                line = shape.line()
                row += [e * self.scene().scale for e in [line.x1() + distx , line.y1() + disty, line.x2() + distx, line.y2() + disty]]
                ret['shapes'].append(row)
            elif type(shape) is Bus:
                row = ['bus']
                line = shape.line()
                row += [e * self.scene().scale for e in [line.x1() + distx , line.y1() + disty, line.x2() + distx, line.y2() + disty]]
                ret['shapes'].append(row)
            elif type(shape) is Circle:
                row = ['c']
                rect = shape.rect()
                row += [ e * self.scene().scale for e in [rect.x()+distx+rect.width()/2, rect.y()+disty+rect.width()/2, rect.width()/2]]
                ret['shapes'].append(row)
            elif type(shape) is Polygon:
                row = ['p']
                row += ['_','_','_','_'] # useless so far
                for point in shape.polygon().toList():
                    row += [(point.x() + distx) * self.scene().scale,
                            (point.y() + disty) * self.scene().scale,
                            ]
                row += [shape.last]
                ret['shapes'].append(row)
            elif type(shape) is Arc:
                row = ['a']
                radius = shape.rect().width()/2 * self.scene().scale
                pos_x = (shape.rect().x()+distx)*self.scene().scale + radius
                pos_y = (shape.rect().y()+disty)*self.scene().scale + radius
                start = shape.startAngle() / 16
                end = shape.spanAngle() /16 + start
                row += [pos_x, pos_y, radius, start*10, end*10]
                ret['shapes'].append(row)
            elif type(shape) is Text:
                row = ['label']
                text = shape.toPlainText()
                dimension = shape.dimension * self.scene().scale
                pos_x = (shape.x() + distx)* self.scene().scale
                pos_y = (shape.y() + +disty+shape.dimension)* self.scene().scale
                row += [pos_x, pos_y, '_', dimension, text]
                ret['shapes'].append(row)

            else:
                pass

        return ret

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

    def contextMenuEvent(self, event):
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
        self.setScale(float(dialog.scale_percentage.text()) / 100)

    def draw(self, scene, model, shapes, devinfo, nextNetIndex, isThumbnail=False):
        dev = devinfo[model]
        nameHead = dev.head
        params = dev.getParamList()
        nameId = self.getAutoNameId(scene, nameHead)
        self.setInstName(nameHead, nameId)
        self.lib = dev.lib
        self.name = nameHead + str(nameId)
        self.model = model
        self.pins = dev.pins
        self.conns = {p:'net{}'.format(nextNetIndex+idx) for idx, p in enumerate(self.pins)}
        self.initial_conns = self.conns.copy()
        for shape_params in shapes:
            shape = self.draw_shape(scene, shape_params)
            if shape is not None:
                self.addToGroup(shape)
                if isinstance(shape, SymbolPin):
                    self.SymbolPins.append(shape)

        if isThumbnail:
            return

        self.params = params
        self.paramText = ParameterText()
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
            if shape_params[-1].lower() == 'f':
                p.setBrush(p.pen.color())
                p.last = 'f'
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
            p.setParent(self)
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

    def isModelVisible(self):
        return self.lib != 'basic'

    def isXInst(self):
        return self.lib == 'pdk'

    def make_by_JSON(self, jsn, scene):
        for k in ['nameHead', 'nameId','name','model','pins','conns','initial_conns','space','lib']:
            setattr(self, k, jsn[k])
        for p in jsn['params']:
            param = DeviceParam()
            param.make_by_JSON(p)
            self.params.append(param)
        for shape in jsn['shapes']:
            p = self.draw_shape(scene, shape)
            if p is not None:
                self.addToGroup(p)
                if isinstance(p, SymbolPin):
                    self.SymbolPins.append(p)

        for idx, status in enumerate(jsn['pins_status']):
            if status is True:
                self.SymbolPins[idx].setConnected()
            else:
                self.SymbolPins[idx].setDisConnected()

        if jsn.get('paramText') is not None:
            self.paramText = ParameterText()
            self.paramText.setPlainText(jsn['paramText'][0])
            self.paramText.setPos(jsn['paramText'][1],jsn['paramText'][2])
            self.addToGroup(self.paramText)

        self.setTransformOriginPoint(jsn.get('distx'), jsn.get('disty'))
        self.setScale(jsn.get('scale'))
        self.setRotation(jsn.get('rotation'))
        t = self.transform()
        t.translate(jsn.get('distx'), jsn.get('disty'))
        t.scale(jsn.get('m11'), jsn.get('m22'))
        t.translate(-jsn.get('distx'), -jsn.get('disty'))
        self.setTransform(t)



class DesignGroup(QGraphicsItemGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.design = None

    def setDesign(self, design):
        self.design = design

    def design(self):
        return self.design

    def contextMenuEvent(self, event):
        if self.design is None:
            return

        dialog = DesignDialog(parent=None,designRect=self)
        dialog.exec()
