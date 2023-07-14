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


class Group(QGraphicsItemGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.id_head = None
        self.id_num = None
        self.id = None
        self.parameter_text = None
        self.parameters = [] # [('','p1'),('param_name','c1')...]
        self.space = ''

    def paint(self, painter, option, widget=None, *args, **kwargs):
        if self.isSelected():
            pen = QPen()
            pen.setStyle(Qt.DotLine)
            pen.setWidth(pen.width()/2)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def setid(self, id_head, id_num):
        self.id_head = id_head
        self.id_num = id_num

    def contextMenuEvent(self, event):
        dialog = ParameterDialog(parent=None, item=self.parameter_text)
        if dialog.exec():
            self.id = dialog.name.text()
            self.parameters = [(v[0], v[1].text()) for v in dialog.values]
            self.set_parameter_text()

            id_head = self.id[0].upper()
            id_num = self.id[1:]
            if re.search('^\d+$', id_num):
                id_num = int(id_num)
                self.setid(id_head, id_num)
            else:
                self.setid(None, None)
        #return super().contextMenuEvent(event)

    def draw(self, scene, sym_type, shapes, params, isThumbnail=False):
        id_head = sym_type[0].upper()
        id_num = self.auto_id(scene, id_head)
        self.setid(id_head, id_num)
        self.id = id_head + str(id_num)
        for shape_params in shapes:
            shape = self.draw_shape(scene, shape_params)
            if shape is not None:
                self.addToGroup(shape)

        if isThumbnail:
            return

        self.parameters = self.parse_params(params)
        self.parameter_text = ParameterText()
        self.set_parameter_text()
        right = self.boundingRect().x() + self.boundingRect().width()
        self.parameter_text.setPos(right,self.boundingRect().y())
        self.addToGroup(self.parameter_text)

    def parse_params(self,params):
        return  [(p.name,p.defVal) for p in params]

    def set_parameter_text(self):
        p = [self.space+self.id]
        for param in self.parameters:
            name, value = param[0], param[1]
            if name == '' or name.lower() == 'value':
                p.append(self.space + value)
            else:
                p.append(self.space+name[0]+'='+value)
        if len(self.parameters) > 1:
            text = '\n'.join(p)
        else:
            text = '\n\n'.join(p)
        self.parameter_text.setPlainText(text)


    def auto_id(self, scene, id_head):
        num_set = set()
        for symbol in scene.symbols:
            if symbol.id_head is not None:
                if id_head == symbol.id_head:
                    if symbol.id_num is not None:
                        num_set.add(symbol.id_num)
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
