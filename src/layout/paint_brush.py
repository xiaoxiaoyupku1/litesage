from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QPen, QFont


class PaintBrushManage(object):

    def __init__(self):
        self.paintbrush_map = {}
        self.colors = [
            Qt.GlobalColor.blue,
            Qt.GlobalColor.green,
            Qt.GlobalColor.red,
            Qt.GlobalColor.yellow,
            Qt.GlobalColor.cyan,
            Qt.GlobalColor.darkMagenta,
            Qt.GlobalColor.darkBlue,
            Qt.GlobalColor.darkGray,
            Qt.GlobalColor.darkGreen,
            Qt.GlobalColor.darkYellow,
        ]
        self.colors_index = 0
        self.paintbrush_container = {}
        self.colors_container = {}
        self.high_light_net_container = {}
        self.highlight_net_colors_index = 0

    def get_color(self, layer_num):
        if layer_num not in self.colors_container:
            if len(self.colors) == self.colors_index:
                self.colors_index = 0
            color = self.colors[self.colors_index]
            self.colors_index += 1
            self.colors_container[layer_num] = color
        return self.colors_container[layer_num]

    def get_highlight_net_color(self, net_name):
        if net_name not in self.colors_container:
            if len(self.colors) == self.highlight_net_colors_index:
                self.highlight_net_colors_index = 0
            color = self.colors[self.highlight_net_colors_index]
            self.highlight_net_colors_index += 1
            self.colors_container[net_name] = color
        return self.colors_container[net_name]

    def get_paintbrush(self, layer_id: str):
        layer_num = layer_id.split('-')[0]
        if layer_num not in self.paintbrush_map:
            color = self.get_color(layer_num)
            pen = QPen()
            brush = QBrush()
            brush.setStyle(Qt.BrushStyle.BDiagPattern)
            brush.setColor(color)
            pen.setColor(color)
            self.paintbrush_map[layer_num] = (pen, brush)

        return self.paintbrush_map[layer_num]

    def get_highlight_net_paintbrush(self, net_name):
        if net_name not in self.high_light_net_container:
            color = self.get_highlight_net_color(net_name)
            pen = QPen()
            brush = QBrush()
            brush.setStyle(Qt.BrushStyle.Dense5Pattern)
            brush.setColor(color)
            pen.setColor(color)
            pen.setWidth(50)
            self.high_light_net_container[net_name] = (pen, brush)

        return self.high_light_net_container[net_name]

    def get_preselect_paintbrush(self):
        if 'preselect' not in self.paintbrush_map:
            color = Qt.GlobalColor.yellow
            pen = QPen()
            brush = QBrush()
            brush.setStyle(Qt.BrushStyle.SolidPattern)
            brush.setColor(color)
            pen.setColor(color)
            pen.setWidth(100)
            self.paintbrush_map['preselect'] = (pen, brush)

        return self.paintbrush_map['preselect']

    def get_selected_paintbrush(self):
        if 'selected' not in self.paintbrush_map:
            color = Qt.GlobalColor.red
            pen = QPen()
            brush = QBrush()
            brush.setStyle(Qt.BrushStyle.SolidPattern)
            brush.setColor(color)
            pen.setColor(color)
            pen.setWidth(100)
            self.paintbrush_map['selected'] = (pen, brush)

        return self.paintbrush_map['selected']

    def get_highlight_polygon_paintbrush(self):
        if 'highlight_polygon_paintbrush' not in self.paintbrush_container:
            pen = QPen()
            pen.setColor(Qt.GlobalColor.yellow)
            brush = QBrush()
            brush.setColor(Qt.GlobalColor.yellow)
            pen.setWidth(100)
            brush.setStyle(Qt.Dense4Pattern)
            self.paintbrush_container['highlight_polygon_paintbrush'] = [pen, brush]
        return self.paintbrush_container['highlight_polygon_paintbrush']

    @staticmethod
    def get_select_text_color():
        return Qt.GlobalColor.red

    @staticmethod
    def get_default_text_color():
        return Qt.GlobalColor.black

    def get_component_bb_paintbrush(self):
        if 'component_bb' not in self.paintbrush_container:
            pen = QPen()
            pen.setColor(Qt.GlobalColor.black)
            pen.setWidth(100)
            brush = QBrush()
            brush.setColor(Qt.GlobalColor.red)
            brush.setStyle(Qt.Dense4Pattern)
            self.paintbrush_container['component_bb'] = [pen, brush]
        return self.paintbrush_container['component_bb']

    def get_component_name_paintbrush(self):
        if 'component_name' not in self.paintbrush_container:
            pen = QPen()
            pen.setColor(Qt.GlobalColor.red)
            brush = QBrush()
            brush.setColor(Qt.GlobalColor.red)
            brush.setStyle(Qt.Dense4Pattern)
            self.paintbrush_container['component_name'] = [pen, brush]
        return self.paintbrush_container['component_name']

    @staticmethod
    def get_temp_add_polygon_pen():
        pen = QPen()
        brush = QBrush()
        brush.setColor(Qt.GlobalColor.green)
        brush.setStyle(Qt.Dense4Pattern)
        pen.setColor(Qt.GlobalColor.green)
        pen.setWidth(50)
        return pen, brush

    @staticmethod
    def get_blank_pen():
        pen = QPen()
        pen.setColor(Qt.GlobalColor.white)
        return pen

    @staticmethod
    def get_text_font(size=200):
        font = QFont()
        font.setPointSize(size)
        return font

    def get_metal_space_paintbrush(self):

        if 'metal_space' not in self.paintbrush_container:
            pen = QPen()
            pen.setColor(Qt.GlobalColor.red)
            brush = QBrush()
            brush.setColor(Qt.GlobalColor.red)
            brush.setStyle(Qt.Dense4Pattern)
            self.paintbrush_container['metal_space'] = [pen, brush]
        return self.paintbrush_container['metal_space']

    def get_select_rectangle_area_paintbrush(self):
        if 'select_rectangle_area' not in self.paintbrush_container:
            pen = QPen()
            pen.setColor(Qt.GlobalColor.red)
            pen.setWidth(100)
            brush = QBrush()
            brush.setColor(Qt.GlobalColor.red)
            brush.setStyle(Qt.Dense4Pattern)
            self.paintbrush_container['select_rectangle_area'] = [pen, brush]
        return self.paintbrush_container['select_rectangle_area']

    def get_x_y_line_paintbrush(self):

        if 'x_y_line' not in self.paintbrush_container:
            pen = QPen()
            pen.setColor(Qt.GlobalColor.red)
            brush = QBrush()
            pen.setWidth(10)
            brush.setColor(Qt.GlobalColor.red)
            brush.setStyle(Qt.Dense4Pattern)
            self.paintbrush_container['x_y_line'] = [pen, brush]
        return self.paintbrush_container['x_y_line']
