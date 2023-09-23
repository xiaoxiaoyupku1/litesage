from PySide6.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsPolygonItem
from src.layout.paint_brush import PaintBrushManage
from PySide6.QtCore import QRectF


class LayoutScene(QGraphicsScene):

    def __init__(self, layout_app, layout_view, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout_app = layout_app
        self.layout_view = layout_view
        self.paintbrush_manage = PaintBrushManage()
        self.polygon_obj_container = {}
        self.net_label_obj_container = {}
        self.label_obj_container = {}
        self.other_label_obj_container = {}
        self.component_label_obj_container = {}
        self.text_name_obj_container = {}
        self.bb = []
        self.bb_polygon_item = None
        self.blank_polygon_item = None

    def create_layout_polygon(self):

        x_list = []
        y_list = []
        for layer_id, pg_list in self.layout_app.gds_manage.polygon_data.items():
            pen, brush = self.paintbrush_manage.get_paintbrush(layer_id)
            if layer_id not in self.polygon_obj_container:
                self.polygon_obj_container[layer_id] = []
            for pg in pg_list:
                x_list.extend([pg.bb[0], pg.bb[2]])
                y_list.extend([pg.bb[1], pg.bb[3]])
                obj = self.addRect(pg.bb[0], pg.bb[1], pg.width, pg.height, pen=pen, brush=brush)
                obj.show()
                self.polygon_obj_container[layer_id].append(obj)
        min_x = min(x_list)
        min_y = min(y_list)
        max_x = max(x_list)
        max_y = max(y_list)
        self.bb = [min_x, min_y, max_x, max_y]
        self.width()
        self.height()
        self.setSceneRect(min_x-self.width(),min_y-self.height(),self.width()*3,self.height()*3)
        return

    def move_all_items(self, shift_x, shift_y):
        for item in self.items():
            x, y = item.pos().x(), item.pos().y()
            x += shift_x
            y += shift_y
            item.setPos(x, y)

    def show_label_by_name(self, net_name):
        for obj in self.text_name_obj_container.get(net_name, []):
            obj.show()

    def hide_label_by_name(self, net_name):
        for obj in self.text_name_obj_container.get(net_name, []):
            obj.hide()

    def show_label_by_layer_id(self, layer_id):
        for obj in self.label_obj_container.get(layer_id,[]):
            obj.show()

    def hide_label_by_layer_id(self, layer_id):
        for obj in self.label_obj_container.get(layer_id, []):
            obj.hide()

    def show_layer_polygon(self, layer_id):
        for obj in self.polygon_obj_container.get(layer_id, []):
            obj.show()

    def hide_layer_polygon(self, layer_id):
        for obj in self.polygon_obj_container.get(layer_id, []):
            obj.hide()

    def create_net_label(self):
        net_layer_id_set = set(self.layout_app.get_layer_list_view_data())
        font = self.paintbrush_manage.get_text_font()
        for layer_id, label_list in self.layout_app.gds_manage.label_data.items():
            if layer_id in net_layer_id_set:
                if layer_id not in self.net_label_obj_container:
                    self.net_label_obj_container[layer_id] = []
                if layer_id not in self.label_obj_container:
                    self.label_obj_container[layer_id] = []
                for label in label_list:
                    obj = QGraphicsTextItem(label.text)
                    obj.setFont(font)
                    obj.setPos(label.x-obj.boundingRect().width()/2, label.y)
                    self.addItem(obj)
                    self.net_label_obj_container[layer_id].append(obj)
                    self.label_obj_container[layer_id].append(obj)
                    if label.text not in self.text_name_obj_container:
                        self.text_name_obj_container[label.text] = []
                    self.text_name_obj_container[label.text].append(obj)