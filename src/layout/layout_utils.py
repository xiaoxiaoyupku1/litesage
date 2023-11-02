from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsPolygonItem
from PySide6.QtGui import QPolygonF
from PySide6.QtCore import QPointF


class LayoutType(object):

    Rectangle = 3
    Polygon = 5
    Text = 8
    Line = 6


class Status(object):
    Normal = 'Normal'
    Delete = 'Delete'


class ItemType(object):
    Shape = 'Shape'
    Text = 'Text'


class LayoutLineItem(QGraphicsLineItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LayoutPolygonItem(QGraphicsPolygonItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer_id = ''
        self.polygon_instance = None
        self.net_item = None
        self.is_show_net = False
        self.is_edit = True

    def delete(self):
        self.polygon_instance.status = Status.Delete
        self.hide()

    def is_delete(self):
        return self.polygon_instance.status == Status.Delete

    def show(self) -> None:
        super(LayoutPolygonItem, self).show()
        self.show_net()

    def hide(self) -> None:
        super(LayoutPolygonItem, self).hide()
        self.hide_net()

    def show_net(self):
        if self.net_item and self.isVisible() and self.is_show_net:
            self.net_item.show()

    def hide_net(self):
        if self.net_item:
            self.net_item.hide()


class LayoutRectItem(QGraphicsRectItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer_id = ''
        self.polygon_instance = None
        self.net_item = None
        self.is_show_net = False
        self.is_edit = True

    def delete(self):
        self.polygon_instance.status = Status.Delete
        self.hide()

    def is_delete(self):
        return self.polygon_instance.status == Status.Delete

    def show(self) -> None:
        super(LayoutRectItem, self).show()
        self.show_net()

    def hide(self) -> None:
        super(LayoutRectItem, self).hide()
        self.hide_net()

    def show_net(self):
        if self.net_item and self.isVisible() and self.is_show_net:
            self.net_item.show()

    def hide_net(self):
        if self.net_item:
            self.net_item.hide()


class LayoutTextItem(QGraphicsTextItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer_id = ''
        self.text_instance = None
        self.is_edit = True

    def delete(self):
        if self.text_instance:
            self.text_instance.status = Status.Delete
        self.hide()

    def is_delete(self):
        return self.text_instance.status == Status.Delete


class Polygon(object):

    def __init__(self, layer_num, data_type, point_list):
        self.layer_num = layer_num
        self.data_type = data_type
        self.layer_id = "{}-{}".format(layer_num, data_type)
        self.point_list = point_list
        self.bb = self.get_bb()
        self.width = self.bb[2] - self.bb[0]
        self.height = self.bb[3] - self.bb[1]
        self.is_polygon = self.get_is_polygon()
        self.layout_item = None
        self.status = Status.Normal
        self.net_name = ''
        self.net_location = None

    def get_graphics_item(self, paintbrush_manage):
        if not self.layout_item:
            pen, brush = paintbrush_manage.get_paintbrush(self.layer_id)
            if self.is_polygon:
                polygon = QPolygonF([QPointF(point[0], -point[1]) for point in self.point_list])
                self.layout_item = LayoutPolygonItem(polygon)
            else:
                self.layout_item = LayoutRectItem(self.bb[0], -self.bb[3], self.width, self.height)
            self.layout_item.setPen(pen)
            self.layout_item.setBrush(brush)
            self.layout_item.layer_id = self.layer_id
            self.layout_item.polygon_instance = self
        return self.layout_item

    def get_temp_graphics_item(self, paintbrush_manage):
        pen, brush = paintbrush_manage.get_paintbrush(self.layer_id)
        layout_item = LayoutRectItem(self.bb[0], -self.bb[3], self.width, self.height)
        layout_item.setPen(pen)
        layout_item.setBrush(brush)
        layout_item.layer_id = self.layer_id
        layout_item.polygon_instance = self
        return layout_item

    @staticmethod
    def create_polygon_by_layer_id(point_list, layer_id: str):
        split_items = layer_id.split('-')
        layer_num = int(split_items[0])
        data_type = int(split_items[1])
        pg = Polygon(layer_num, data_type, point_list)
        return pg

    @staticmethod
    def get_point_list_by_bb(bb):
        return [
            (bb[0], bb[1]),
            (bb[0], bb[3]),
            (bb[2], bb[3]),
            (bb[2], bb[1]),
        ]

    def get_text_item(self, paintbrush_manage, text_layer_id=None):
        font = paintbrush_manage.get_text_font()
        text_item = LayoutTextItem(self.net_name)
        text_item.setFont(font)
        text_item.setPos(self.net_location[0] - text_item.boundingRect().width() / 2,
                         -self.net_location[1] - text_item.boundingRect().height() / 2)
        if text_layer_id:
            text_item.layer_id = text_layer_id
        else:
            text_item.layer_id = self.layer_id
        return text_item

    @staticmethod
    def get_pg_list_by_bb_list(bb_list, layer_id: str):
        pg_list = []
        layer_id_split = layer_id.split('-')
        layer_num = int(layer_id_split[0])
        data_type = int(layer_id_split[1])
        for bb in bb_list:
            pg_list.append(Polygon(layer_num, data_type, Polygon.get_point_list_by_bb(bb)))
        return pg_list

    def get_bb(self):
        x_list = []
        y_list = []
        for point in self.point_list:
            x_list.append(point[0])
            y_list.append(point[1])
        bb = [min(x_list), min(y_list), max(x_list), max(y_list)]
        return bb

    def get_is_polygon(self):
        point_list = self.point_list + [self.point_list[0]]
        if len(point_list) == 5:
            for b_point, a_point in zip(point_list[:-1], point_list[1:]):
                if b_point[0] == a_point[0]:
                    if b_point[1] == a_point[1]:
                        return True
                elif b_point[1] == a_point[1]:
                    if b_point[0] == a_point[0]:
                        return True
                else:
                    return True
            return False
        else:
            return True

    @staticmethod
    def rect_overlap(bb1, bb2):

        pg1_min_x, pg1_max_x = bb1[0], bb1[2]
        pg1_min_y, pg1_max_y = bb1[1], bb1[3]
        pg2_min_x, pg2_max_x = bb2[0], bb2[2]
        pg2_min_y, pg2_max_y = bb2[1], bb2[3]

        if max(pg2_min_x, pg2_max_x) <= min(pg1_min_x, pg1_max_x):
            return False
        elif min(pg2_min_x, pg2_max_x) >= max(pg1_min_x, pg1_max_x):
            return False
        elif max(pg2_min_y, pg2_max_y) <= min(pg1_min_y, pg1_max_y):
            return False
        elif min(pg2_min_y, pg2_max_y) >= max(pg1_min_y, pg1_max_y):
            return False
        else:
            return True

    @staticmethod
    def get_overlap_bb(bb1, bb2):
        min_x_1 = bb1[0]
        min_y_1 = bb1[1]
        max_x_1 = bb1[2]
        max_y_1 = bb1[3]
        min_x_2 = bb2[0]
        min_y_2 = bb2[1]
        max_x_2 = bb2[2]
        max_y_2 = bb2[3]

        if Polygon.rect_overlap(bb1, bb2):
            intersection_pg = [max(min_x_1, min_x_2), max(min_y_1, min_y_2),
                               min(max_x_1, max_x_2), min(max_y_1, max_y_2)]
            return intersection_pg
        else:
            return []


class Label(object):

    def __init__(self, layer_num, data_type, text, x, y):
        self.layer_num = layer_num
        self.data_type = data_type
        self.layer_id = "{}-{}".format(layer_num, data_type)
        self.x = x
        self.y = y
        self.text = text
        self.layout_item = None
        self.status = Status.Normal
        self.type = ItemType.Text

    def get_graphics_item(self, paintbrush_manage):
        if not self.layout_item:
            font = paintbrush_manage.get_text_font()
            self.layout_item = LayoutTextItem(self.text)
            self.layout_item.setFont(font)
            self.layout_item.setPos(self.x - self.layout_item.boundingRect().width() / 2,
                                    -self.y - self.layout_item.boundingRect().height() / 2)
            self.layout_item.layer_id = self.layer_id
            self.layout_item.text_instance = self
        return self.layout_item


class OnGrid(object):

    @staticmethod
    def on_grid_ceil(on_grid, value):
        if int(value) % on_grid == 0:
            return int(value)
        return int(value) + (on_grid - int(value) % on_grid)

    @staticmethod
    def on_grid_floor(on_grid, value):
        if int(value) % on_grid == 0:
            return int(value)
        return int(value) - int(value) % on_grid


if __name__ == '__main__':
    bbox1 = [0, 0, 100, 100]
    bbox2 = [50, 50, 150, 150]
    Polygon.get_overlap_bb(bbox1, bbox2)
