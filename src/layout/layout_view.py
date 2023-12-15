from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen
from src.layout.layout_utils import LayoutType


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
        self.scale(scale, scale)
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
        self.resize_rectangle_pen_width()
        self.resize_polygon_pen_width()
        self.resize_line_pen_width()

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
