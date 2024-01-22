from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen
from src.layout.layout_utils import LayoutType
from PySide6.QtGui import QBrush, QPen, QFont
from src.layout.layout_utils import TextType
from PySide6.QtGui import QKeyEvent


class LayoutView(QGraphicsView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setStyleSheet("padding: 0px; border: 0px;")
        self.zoom_in_sx = 1.2
        self.zoom_in_sy = 1.2
        self.zoom_out_sx = 1.0 / 1.2
        self.zoom_out_sy = 1.0 / 1.2
        self.layout_scene = None
        self.font_size = 5
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

    def resize_rectangle_pen_width(self):
        pen_width = int(self.mapToScene(0, 0, 1, 1)[2].x() - self.mapToScene(0, 0, 1, 1)[0].x())
        for item in [item for item in self.scene().items() if item.type() == LayoutType.Rectangle]:
            pen = QPen(item.pen().color(), pen_width)
            item.setPen(pen)

    def resize_polygon_pen_width(self):
        pen_width = int(self.mapToScene(0, 0, 1, 1)[2].x() - self.mapToScene(0, 0, 1, 1)[0].x())
        for item in [item for item in self.scene().items() if item.type() == LayoutType.Polygon]:
            pen = QPen(item.pen().color(), pen_width)
            item.setPen(pen)

    def resize_line_pen_width(self):
        pen_width = int(self.mapToScene(0, 0, 1, 1)[2].x() - self.mapToScene(0, 0, 1, 1)[0].x())
        bbox_width = int(self.mapToScene(0, 0, 3, 3)[2].x() - self.mapToScene(0, 0, 3, 3)[0].x())
        for item in [item for item in self.scene().items() if item.type() == LayoutType.Line]:
            if hasattr(item, 'is_bbox') and item.is_bbox:
                pen = QPen(item.pen().color(), bbox_width)
            else:
                pen = QPen(item.pen().color(), pen_width)
            item.setPen(pen)

    def center_display(self):
        self.resetTransform()
        width = self.layout_scene.width()
        height = self.layout_scene.height()
        if width > height:
            scale = (self.width()/width)
        else:
            scale = (self.height() / height)
        scale *= 2.5
        self.scale(scale, scale)
        x_set = set()
        y_set = set()
        while True:
            x = self.mapFromScene(self.scene().bb[0], self.scene().bb[1]).x()
            if x in x_set:
                break
            if 50 < x < 100:
                break
            if x > 100:
                self.keyPressEvent(QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Right, Qt.NoModifier))
            else:
                self.keyPressEvent(QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Left, Qt.NoModifier))
            x_set.add(x)
        while True:
            y = self.mapFromScene(self.scene().bb[0], self.scene().bb[1]).y()
            if y in y_set:
                break
            if 50 < y < 100:
                break
            if y > 100:
                self.keyPressEvent(QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Down, Qt.NoModifier))
            else:
                self.keyPressEvent(QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Up, Qt.NoModifier))
            y_set.add(y)
        self.resize_pen_width()

    def key_press_f(self, event):
        self.center_display()

    def keyPressEvent(self, event):

        if hasattr(self, "key_press_{}".format(event.text())):
            exec('self.key_press_{}(event)'.format(event.text()))
        elif hasattr(self, "key_press_uppercase_{}".format(event.text().lower())):
            exec('self.key_press_uppercase_{}(event)'.format(event.text().lower()))
        return super(LayoutView, self).keyPressEvent(event)

    def resize_pen_width(self):
        pen_width = int(self.mapToScene(0, 0, 1, 1)[2].x() - self.mapToScene(0, 0, 1, 1)[0].x())
        for item in self.scene().items():
            if item.type() == LayoutType.Rectangle:
                pen = QPen(item.pen().color(), pen_width)
                item.setPen(pen)
            elif item.type() == LayoutType.Polygon:
                pen = QPen(item.pen().color(), pen_width)
                item.setPen(pen)
            elif item.type() == LayoutType.Line:
                pen_width = int(self.mapToScene(0, 0, 1, 1)[2].x() - self.mapToScene(0, 0, 1, 1)[0].x())
                bbox_width = int(self.mapToScene(0, 0, 3, 3)[2].x() - self.mapToScene(0, 0, 3, 3)[0].x())
                if hasattr(item, 'is_bbox') and item.is_bbox:
                    pen = QPen(item.pen().color(), bbox_width)
                else:
                    pen = QPen(item.pen().color(), pen_width)
                item.setPen(pen)
            elif item.type() == LayoutType.Text and hasattr(item, 'text_type') and item.text_type == TextType.Component:
                pen_width = int(self.mapToScene(0, 0, self.font_size, self.font_size)[2].x() -
                                self.mapToScene(0, 0, self.font_size, self.font_size)[0].x())
                font = QFont()
                font.setPointSize(pen_width)
                item.setFont(font)
                item.setPos(item.origin_x - item.boundingRect().width() / 2, -item.origin_y - item.boundingRect().height() / 2)

        # self.resize_rectangle_pen_width()
        # self.resize_polygon_pen_width()
        # self.resize_line_pen_width()

    def set_font_size(self, value):
        self.font_size = value
        self.resize_pen_width()

    def wheelEvent(self, event) -> None:
        if len(self.scene().items()) > 0:
            wheel_delta_value = event.angleDelta().y()
            if wheel_delta_value > 0:
                self.scale(self.zoom_in_sx, self.zoom_in_sy)
            else:
                self.scale(self.zoom_out_sx, self.zoom_out_sy)
            self.layout_scene.update()
            self.update()
            self.resize_pen_width()

    def zoomIn(self):
        self.scale(self.zoom_in_sx, self.zoom_in_sy)
        self.layout_scene.update()
        self.update()
        self.resize_pen_width()

    def zoomOut(self):
        self.scale(self.zoom_out_sx, self.zoom_out_sy)
        self.layout_scene.update()
        self.update()
        self.resize_pen_width()