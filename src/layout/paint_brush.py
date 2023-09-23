from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QPen, QFont


class PaintBrushManage(object):

    def __init__(self):
        self.paintbrush_map = {}
        self.colors = [Qt.GlobalColor.blue, Qt.GlobalColor.green, Qt.GlobalColor.red, Qt.GlobalColor.yellow]
        self.colors_index = 0

    def get_color(self):
        if len(self.colors) == self.colors_index:
            self.colors_index = 0
        color = self.colors[self.colors_index]
        self.colors_index += 1
        return color

    def get_paintbrush(self, layer_id):
        if layer_id not in self.paintbrush_map:
            color = self.get_color()
            pen = QPen()
            brush = QBrush()
            brush.setStyle(Qt.Dense4Pattern)
            brush.setColor(color)
            pen.setColor(color)
            pen.setWidth(1)
            self.paintbrush_map[layer_id] = (pen, brush)

        return self.paintbrush_map[layer_id]

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
