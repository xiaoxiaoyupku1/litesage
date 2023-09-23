from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt


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
        self.canvas_zoom_coefficient = 1
        self.canvas_zoom_variable_x = 0
        self.canvas_zoom_variable_y = 0
        self.canvas_enlarge_scale = 1.01
        self.canvas_shrink_scale = 1/1.01

    def center_display(self):
        width = self.layout_scene.width()
        height = self.layout_scene.height()
        if width > height:

            scale = self.width()/width
        else:
            scale = self.height() / width

        self.scale(scale, scale)

    def keyPressEvent(self, event):

        if event.text() == 'f':
            print('hot key f')
            # self.center_display()
        return super(LayoutView, self).keyPressEvent(event)

    def wheelEvent(self, event) -> None:
        if len(self.scene().items()) > 0:
            wheel_delta_value = event.angleDelta().y()
            if wheel_delta_value > 0:
                self.scale(self.zoom_in_sx, self.zoom_in_sy)
            else:
                self.scale(self.zoom_out_sx, self.zoom_out_sy)
            self.update()

    def fit(self, scene):
        self.fitInView(scene.itemsBoundingRect(), Qt.KeepAspectRatio)