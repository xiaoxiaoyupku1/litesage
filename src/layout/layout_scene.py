from PySide6.QtWidgets import QGraphicsScene, QMessageBox
from src.layout.paint_brush import PaintBrushManage
from PySide6.QtGui import Qt, QTransform
from src.layout.layout_application import LayoutApplication
from src.layout.layout_utils import Polygon, Label
from src.layout.layout_utils import LayoutRectItem, LayoutTextItem, LayoutLineItem
from src.layout.layout_utils import LayoutType
from src.layout.config import forbidden_layer_id, terminal_layer_id
import re


class SceneDirection(object):
    Up = 'Up'
    Down = 'Down'
    Left = 'Left'
    Right = 'Right'
    Vertical = 'Vertical'
    Horizontal = 'Horizontal'


class SceneMode(object):
    Normal = 'Normal'
    PrePath = 'PrePath'
    AddPath = 'AddPath'
    EditVia = 'EditVia'


class RoutingInfo(object):

    def __init__(self):
        self.net_name = ''
        self.layer_id = ''
        self.line_width = 0
        self.start_x = 0
        self.start_y = 0
        self.direction = SceneDirection.Horizontal
        self.last_direction = None
        self.is_add_net_text = False

    def set_info(self, net_name, layer_id, line_width, is_add_net_text):
        self.net_name = net_name
        self.layer_id = layer_id
        self.line_width = line_width
        self.is_add_net_text = is_add_net_text

    def set_start_position(self, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y


class ShowMode(object):

    Simple = 'Simple'
    Detail = 'Detail'


class LayoutScene(QGraphicsScene):

    def __init__(self, layout_app: LayoutApplication, layout_view, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout_app = layout_app
        self.layout_view = layout_view
        self.main_window = main_window
        self.paintbrush_manage = PaintBrushManage()
        self.polygon_obj_container = {}
        self.net_label_obj_container = {}
        self.label_obj_container = {}
        self.other_label_obj_container = {}
        self.component_label_obj_container = {}
        self.polygon_net_container = {}
        self.bb = []
        self.bb_polygon_item = None
        self.blank_polygon_item = None
        self.mode = SceneMode.Normal
        self.routing_info = RoutingInfo()
        self.highlight_item = None
        self.routing_item = None
        self.path_polygon_list = []
        self.path_label_list = []
        self.temp_routing_polygon_list = []
        self.net_name_list = []
        self.delete_item_list = []
        self.preselect_item = None
        self.selected_item_list = []
        self.show_mode = ShowMode.Detail
        self.component_bb_container = {}
        self.component_name_container = {}
        self.x_line_item = None
        self.y_line_item = None
        self.first_routing_item = None
        self.last_routing_item = None
        self.mouse_start_point = None
        self.select_rectangle_area_item = None
        self.metal_space_item1 = None
        self.metal_space_item2 = None
        self.metal_space_item3 = None

    def clear_routing_polygons(self):
        self.path_polygon_list = []

    def get_net_name_list(self):
        if not self.net_name_list:
            self.net_name_list = [net for net in self.polygon_net_container.keys()]
            self.net_name_list.sort()
        return self.net_name_list

    def reset(self):
        self.clear()
        self.paintbrush_manage = PaintBrushManage()
        self.polygon_obj_container = {}
        self.net_label_obj_container = {}
        self.label_obj_container = {}
        self.other_label_obj_container = {}
        self.component_label_obj_container = {}
        self.bb = []
        self.bb_polygon_item = None
        self.blank_polygon_item = None
        self.mode = SceneMode.Normal
        self.routing_info = RoutingInfo()
        self.highlight_item = None
        self.routing_item = None
        self.path_polygon_list = []
        self.temp_routing_polygon_list = []
        self.net_name_list = []
        self.polygon_net_container = {}
        self.component_bb_container = {}
        self.component_name_container = {}

    def add_layout_polygon(self, net_name, layer_id, line_width, is_add_net_text):
        self.mode = SceneMode.PrePath
        self.routing_info.set_info(net_name, layer_id, line_width, is_add_net_text)

    def handle_pre_add_path_move_event(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if item and self.highlight_item != item and item.type() == 3 and hasattr(item, 'layer_id') and \
                self.layout_app.config.is_metal(item.layer_id) and \
                self.routing_info.net_name == item.polygon_instance.net_name:
            pen, _ = self.paintbrush_manage.get_x_y_line_paintbrush()
            x, y = item.boundingRect().x(), item.boundingRect().y()
            width, height = item.boundingRect().width(), item.boundingRect().height()
            center_y = y + height/2
            center_x = x + width/2
            if self.x_line_item:
                self.x_line_item.setLine(x, center_y, x+width, center_y)
            else:
                self.x_line_item = self.addLine(x, center_y, x+width, center_y, pen=pen)
            if self.y_line_item:
                self.y_line_item.setLine(center_x, y, center_x, y+height)
            else:
                self.y_line_item = self.addLine(center_x, y, center_x, y+height, pen=pen)
            self.x_line_item.show()
            self.y_line_item.show()
            x, y = item.boundingRect().x(), item.boundingRect().y()
            width, height = item.boundingRect().width(), item.boundingRect().height()
            self.first_routing_item = item
            if self.highlight_item:
                self.highlight_item.setRect(x, y, width, height)
            else:
                pen, _ = self.paintbrush_manage.get_highlight_polygon_paintbrush()
                self.highlight_item = self.addRect(x, y, width, height, pen)
            self.highlight_item.show()
        elif self.highlight_item != item:
            if self.x_line_item:
                self.x_line_item.hide()
            if self.y_line_item:
                self.y_line_item.hide()
            if self.highlight_item:
                self.highlight_item.hide()
        else:
            if self.x_line_item:
                self.x_line_item.show()
            if self.y_line_item:
                self.y_line_item.show()
            if self.highlight_item:
                self.highlight_item.show()

    def draw_metal_space_line(self, x, y, width, height, direction):
        line_width = self.routing_info.line_width
        metal_space = self.layout_app.config.get_metal_space(self.routing_info.layer_id)

        if self.metal_space_item1 is None:
            pen, _ = self.paintbrush_manage.get_metal_space_paintbrush()
            self.metal_space_item1 = LayoutLineItem(0, 0, 100, 100)
            self.metal_space_item2 = LayoutLineItem(0, 0, 100, 100)
            self.metal_space_item3 = LayoutLineItem(0, 0, 100, 100)
            self.addItem(self.metal_space_item1)
            self.addItem(self.metal_space_item2)
            self.addItem(self.metal_space_item3)
            self.metal_space_item1.setPen(pen)
            self.metal_space_item2.setPen(pen)
            self.metal_space_item3.setPen(pen)
        if direction == SceneDirection.Left:
            self.metal_space_item1.setLine(x-metal_space, y, x-metal_space, y+line_width)
            self.metal_space_item2.setLine(x, y+line_width+metal_space, x+line_width, y+line_width+metal_space)
            self.metal_space_item3.setLine(x, y-metal_space, x+line_width, y-metal_space)
        elif direction == SceneDirection.Right:
            self.metal_space_item1.setLine(x+width+metal_space, y, x+width+metal_space, y+line_width)
            self.metal_space_item2.setLine(x+width-line_width, y-metal_space, x+width, y-metal_space)
            self.metal_space_item3.setLine(x+width-line_width, y+metal_space+line_width,
                                           x+width, y+metal_space+line_width)
        elif direction == SceneDirection.Up:
            self.metal_space_item1.setLine(x, y-metal_space, x+line_width, y-metal_space)
            self.metal_space_item2.setLine(x-metal_space, y+line_width, x-metal_space, y)
            self.metal_space_item3.setLine(x+line_width+metal_space, y+line_width, x+line_width+metal_space, y)
        else:
            self.metal_space_item1.setLine(x, y+height+metal_space, x+line_width, y+height+metal_space)
            self.metal_space_item2.setLine(x+line_width+metal_space, y+height, x+line_width+metal_space,
                                           y+height-line_width)
            self.metal_space_item3.setLine(x-metal_space, y+height, x-metal_space, y+height-line_width)

    def handle_add_path_move_event(self, event):
        event_x = event.scenePos().x()
        event_y = event.scenePos().y()
        if abs(event_x - self.routing_info.start_x) > abs(event_y - self.routing_info.start_y):
            width = self.layout_app.config.on_grid_value_floor(abs(event_x - self.routing_info.start_x))
            height = self.routing_info.line_width
            if event_x - self.routing_info.start_x < 0:
                if self.routing_info.last_direction is None or self.routing_info.last_direction == SceneDirection.Left \
                        or self.routing_info.last_direction == SceneDirection.Right:
                    x = event_x
                    y = self.routing_info.start_y - self.routing_info.line_width / 2
                elif self.routing_info.last_direction == SceneDirection.Up:
                    x = event_x
                    width += self.routing_info.line_width / 2
                    y = self.routing_info.start_y
                else:
                    x = event_x
                    width += self.routing_info.line_width / 2
                    y = self.routing_info.start_y - height
                direction = SceneDirection.Left
            else:
                if self.routing_info.last_direction is None or self.routing_info.last_direction == SceneDirection.Left \
                        or self.routing_info.last_direction == SceneDirection.Right:
                    x = self.routing_info.start_x
                    y = self.routing_info.start_y - self.routing_info.line_width / 2
                elif self.routing_info.last_direction == SceneDirection.Up:
                    x = self.routing_info.start_x - self.routing_info.line_width / 2
                    y = self.routing_info.start_y
                    width += self.routing_info.line_width / 2
                else:
                    x = self.routing_info.start_x - self.routing_info.line_width / 2
                    y = self.routing_info.start_y - height
                    width += self.routing_info.line_width / 2
                direction = SceneDirection.Right

        else:
            width = self.routing_info.line_width
            height = self.layout_app.config.on_grid_value_floor(abs(event_y - self.routing_info.start_y))
            if event_y - self.routing_info.start_y < 0:
                if self.routing_info.last_direction is None or self.routing_info.last_direction == SceneDirection.Up \
                        or self.routing_info.last_direction == SceneDirection.Down:
                    x = self.routing_info.start_x - self.routing_info.line_width / 2
                    y = self.layout_app.config.on_grid_value_floor(event.scenePos().y())
                elif self.routing_info.last_direction == SceneDirection.Left:
                    x = self.routing_info.start_x
                    y = self.layout_app.config.on_grid_value_floor(event.scenePos().y())
                    height += self.routing_info.line_width / 2
                else:
                    x = self.routing_info.start_x - self.routing_info.line_width
                    y = self.layout_app.config.on_grid_value_floor(event.scenePos().y())
                    height += self.routing_info.line_width / 2
                direction = SceneDirection.Up
            else:
                if self.routing_info.last_direction is None or self.routing_info.last_direction == SceneDirection.Up \
                        or self.routing_info.last_direction == SceneDirection.Down:
                    x = self.routing_info.start_x - self.routing_info.line_width / 2
                    y = self.routing_info.start_y
                elif self.routing_info.last_direction == SceneDirection.Left:
                    x = self.routing_info.start_x
                    y = self.routing_info.start_y - self.routing_info.line_width / 2
                    height += self.routing_info.line_width / 2
                else:
                    x = self.routing_info.start_x - self.routing_info.line_width
                    y = self.routing_info.start_y - self.routing_info.line_width / 2
                    height += self.routing_info.line_width / 2
                direction = SceneDirection.Down
        if self.routing_item:
            self.routing_item.setRect(x, y, width, height)
        else:
            pen, brush = self.paintbrush_manage.get_paintbrush(self.routing_info.layer_id)
            self.routing_item = self.addRect(x, y, height, width, pen, brush)
        self.draw_metal_space_line(x, y, width, height, direction)

    def handle_swipe_to_select(self, event):
        if self.mouse_start_point:
            x0, y0 = self.mouse_start_point
            x1, y1 = event.scenePos().x(), event.scenePos().y()
            if x1 < x0:
                x0, x1 = x1, x0
            if y1 < y0:
                y0, y1 = y1, y0
            width = x1-x0
            height = y1-y0
            items = self.items(x0, y0, width, height, Qt.ItemSelectionMode.ContainsItemShape,
                               Qt.SortOrder.AscendingOrder, QTransform())
            if items:
                for item in self.selected_item_list:
                    self.reset_item(item)
                self.selected_item_list.clear()
                for item in items:
                    if item.is_edit:
                        if item.type() in [LayoutType.Rectangle, LayoutType.Polygon] :
                            pen, _ = self.paintbrush_manage.get_selected_paintbrush()
                            item.setPen(pen)
                            self.selected_item_list.append(item)
                        elif item.type() == LayoutType.Text:
                            item.setDefaultTextColor(self.paintbrush_manage.get_select_text_color())
                            self.selected_item_list.append(item)

    def draw_swipe_select_rectangle(self, event):
        if self.mouse_start_point:
            x0, y0 = self.mouse_start_point
            x1, y1 = event.scenePos().x(), event.scenePos().y()
            if x1 < x0:
                x0, x1 = x1, x0
            if y1 < y0:
                y0, y1 = y1, y0
            width = x1 - x0
            height = y1 - y0
            if self.select_rectangle_area_item:
                self.select_rectangle_area_item.setRect(x0, y0, width, height)
            else:
                pen, _ = self.paintbrush_manage.get_select_rectangle_area_paintbrush()
                self.select_rectangle_area_item = self.addRect(x0, y0, width, height, pen=pen)

    def display_mouse_position(self, event):
        txt = "{} : {}".format(int(round(event.scenePos().x())), -int(round(event.scenePos().y())))
        self.main_window.ui.label.setText(txt)

    def mouseMoveEvent(self, event):
        if self.mode == SceneMode.PrePath:
            self.handle_pre_add_path_move_event(event)
        elif self.mode == SceneMode.AddPath:
            self.handle_add_path_move_event(event)
        else:
            self.draw_swipe_select_rectangle(event)
        self.display_mouse_position(event)
        return super(LayoutScene, self).mouseMoveEvent(event)

    def reset_temp_item(self):
        if self.preselect_item:
            self.removeItem(self.preselect_item)
            self.preselect_item = None
        for item in self.selected_item_list:
            self.reset_item(item)
            item.show()
        if self.x_line_item:
            self.removeItem(self.x_line_item)
            self.x_line_item = None
        if self.y_line_item:
            self.removeItem(self.y_line_item)
            self.y_line_item = None
        if self.routing_item:
            self.removeItem(self.routing_item)
            self.routing_item = None
        if self.metal_space_item1:
            self.removeItem(self.metal_space_item1)
            self.removeItem(self.metal_space_item2)
            self.removeItem(self.metal_space_item3)
            self.metal_space_item1 = None
            self.metal_space_item2 = None
            self.metal_space_item3 = None

    def key_press_esc(self, event):
        self.reset_temp_item()
        message = ''
        if self.mode == SceneMode.AddPath or self.mode == SceneMode.PrePath:
            message = "Exit Path Mode!"
        elif self.mode == SceneMode.EditVia:
            message = 'Exit Via Mode!'
        self.mode = SceneMode.Normal
        self.main_window.refresh_layer_list_view()
        if message:
            QMessageBox.information(self.layout_view, "Edit Mode", message)

    def refresh_canvas(self):
        selected_layer_id_list = self.main_window.get_selected_layer_id_list()

        if self.show_mode == ShowMode.Detail:
            for layer_id in selected_layer_id_list:
                self.show_layer_polygon(layer_id)
                self.show_label_by_layer_id(layer_id)
        else:
            self.show_component_bb()
            self.show_component_name_text()
            for layer_id in selected_layer_id_list:
                self.hide_layer_polygon(layer_id)
                self.hide_label_by_layer_id(layer_id)

    def key_press_o(self, event):
        if self.mode == SceneMode.Normal:
            self.mode = SceneMode.EditVia
            QMessageBox.information(self.layout_view, "Edit Mode", "Enter Via Mode!")

    def key_press_down(self, event):
        if self.mode == SceneMode.AddPath:
            lower_layer_id = self.layout_app.config.get_lower_layer_id(self.routing_info.layer_id)
            if lower_layer_id:
                if self.last_routing_item:
                    if not self.layout_app.config.is_jump(self.last_routing_item.layer_id, lower_layer_id):
                        return
                if self.first_routing_item:
                    if not self.layout_app.config.is_jump(self.first_routing_item.layer_id, lower_layer_id):
                        return
                self.routing_info.layer_id = lower_layer_id
                if self.routing_item:
                    pen, brush = self.paintbrush_manage.get_paintbrush(lower_layer_id)
                    self.routing_item.setPen(pen)
                    self.routing_item.setBrush(brush)

    def key_press_up(self, event):
        if self.mode == SceneMode.AddPath:
            upper_layer_id = self.layout_app.config.get_upper_layer_id(self.routing_info.layer_id)
            if upper_layer_id:
                if self.last_routing_item:
                    if not self.layout_app.config.is_jump(self.last_routing_item.layer_id, upper_layer_id):
                        return
                if self.first_routing_item:
                    if not self.layout_app.config.is_jump(self.first_routing_item.layer_id, upper_layer_id):
                        return
                self.routing_info.layer_id = upper_layer_id
                if self.routing_item:
                    pen, brush = self.paintbrush_manage.get_paintbrush(upper_layer_id)
                    self.routing_item.setPen(pen)
                    self.routing_item.setBrush(brush)

    def key_press_ctrl_f(self, event):
        self.show_mode = ShowMode.Simple
        self.refresh_canvas()

    def key_press_shift_f(self, event):
        self.show_mode = ShowMode.Detail
        self.refresh_canvas()

    def key_press_delete(self, *args):

        for item in self.selected_item_list:
            item.delete()
        self.selected_item_list.clear()
        self.main_window.update_layer_list_view()

    def key_press_enter(self, *args):
        if self.mode == SceneMode.AddPath:
            self.reset_temp_item()
            self.mode = SceneMode.PrePath

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_F:
                self.key_press_ctrl_f(event)
        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            if event.key() == Qt.Key.Key_F:
                self.key_press_shift_f(event)
        elif hasattr(self, "key_press_{}".format(event.text())):
            exec('self.key_press_{}(event)'.format(event.text()))
        elif hasattr(self, "key_press_uppercase_{}".format(event.text().lower())):
            exec('self.key_press_uppercase_{}(event)'.format(event.text().lower()))
        elif event.key() == Qt.Key.Key_Escape:
            self.key_press_esc(event)
        elif event.key() == Qt.Key.Key_Up:
            self.key_press_up(event)
            if self.mode == SceneMode.AddPath:
                return
        elif event.key() == Qt.Key.Key_Down:
            self.key_press_down(event)
            if self.mode == SceneMode.AddPath:
                return
        elif event.key() == Qt.Key.Key_Delete:
            self.key_press_delete(event)
        elif event.key() == Qt.Key.Key_Return:
            self.key_press_enter(event)
        return super(LayoutScene, self).keyPressEvent(event)

    @staticmethod
    def get_points(x0, y0, width, height):
        x1 = x0 + width
        y1 = y0 + height

        x0, y0, x1, y1 = x0, -y1, x1, -y0

        return [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]

    def handle_path_left_button_press_event(self, event):
        if self.routing_item:
            event_x = self.layout_app.config.on_grid_value_floor(event.scenePos().x())
            event_y = self.layout_app.config.on_grid_value_floor(event.scenePos().y())
            add_length = 0
            if self.last_routing_item and self.last_routing_item.layer_id != self.routing_info.layer_id:
                add_length = self.layout_app.config.get_minimum_overlap_length(
                    self.last_routing_item.layer_id, self.routing_info.layer_id)
            if abs(event_x - self.routing_info.start_x) > abs(event_y - self.routing_info.start_y):
                width = self.layout_app.config.on_grid_value_floor(abs(event_x - self.routing_info.start_x))
                height = self.routing_info.line_width
                if event_x - self.routing_info.start_x < 0:
                    if self.routing_info.last_direction is None or self.routing_info.last_direction == \
                            SceneDirection.Left or self.routing_info.last_direction == SceneDirection.Right:
                        x = event_x
                        y = self.routing_info.start_y-self.routing_info.line_width/2
                        if self.routing_info.last_direction is not None:
                            width += add_length
                    elif self.routing_info.last_direction == SceneDirection.Up:
                        x = event_x
                        width += self.routing_info.line_width/2
                        y = self.routing_info.start_y
                        self.routing_info.start_y += self.routing_info.line_width/2
                    else:
                        x = event_x
                        width += self.routing_info.line_width / 2
                        y = self.routing_info.start_y - height
                        self.routing_info.start_y -= self.routing_info.line_width / 2

                    self.routing_info.last_direction = SceneDirection.Left
                else:
                    if self.routing_info.last_direction is None or self.routing_info.last_direction == \
                            SceneDirection.Left or self.routing_info.last_direction == SceneDirection.Right:
                        x = self.routing_info.start_x
                        y = self.routing_info.start_y-self.routing_info.line_width/2
                        if self.routing_info.last_direction is not None:
                            width += add_length
                            x -= add_length
                    elif self.routing_info.last_direction == SceneDirection.Up:
                        x = self.routing_info.start_x - self.routing_info.line_width/2
                        y = self.routing_info.start_y
                        width += self.routing_info.line_width / 2
                        self.routing_info.start_y += self.routing_info.line_width / 2
                    else:
                        x = self.routing_info.start_x - self.routing_info.line_width/2
                        y = self.routing_info.start_y - height
                        width += self.routing_info.line_width / 2
                        self.routing_info.start_y -= self.routing_info.line_width / 2
                    self.routing_info.last_direction = SceneDirection.Right
                self.routing_info.start_x = event_x
            else:
                width = self.routing_info.line_width
                height = self.layout_app.config.on_grid_value_floor(abs(event_y - self.routing_info.start_y))
                if event_y - self.routing_info.start_y < 0:
                    if self.routing_info.last_direction is None or self.routing_info.last_direction == \
                            SceneDirection.Up or self.routing_info.last_direction == SceneDirection.Down:
                        x = self.routing_info.start_x - self.routing_info.line_width/2
                        y = self.layout_app.config.on_grid_value_floor(event.scenePos().y())
                        if self.routing_info.last_direction is not None:
                            height += add_length
                    elif self.routing_info.last_direction == SceneDirection.Left:
                        x = self.routing_info.start_x
                        y = self.layout_app.config.on_grid_value_floor(event.scenePos().y())
                        height += self.routing_info.line_width/2
                        self.routing_info.start_x += self.routing_info.line_width/2
                    else:
                        x = self.routing_info.start_x - self.routing_info.line_width
                        y = self.layout_app.config.on_grid_value_floor(event.scenePos().y())
                        height += self.routing_info.line_width / 2
                        self.routing_info.start_x -= self.routing_info.line_width/2
                    self.routing_info.last_direction = SceneDirection.Up
                else:
                    if self.routing_info.last_direction is None or self.routing_info.last_direction == \
                            SceneDirection.Up or self.routing_info.last_direction == SceneDirection.Down:
                        x = self.routing_info.start_x - self.routing_info.line_width/2
                        y = self.routing_info.start_y
                        if self.routing_info.last_direction is not None:
                            height += add_length
                            y -= add_length
                    elif self.routing_info.last_direction == SceneDirection.Left:
                        x = self.routing_info.start_x
                        y = self.routing_info.start_y - self.routing_info.line_width/2
                        height += self.routing_info.line_width / 2
                        self.routing_info.start_x += self.routing_info.line_width / 2
                    else:
                        x = self.routing_info.start_x - self.routing_info.line_width
                        y = self.routing_info.start_y - self.routing_info.line_width/2
                        height += self.routing_info.line_width / 2
                        self.routing_info.start_x -= self.routing_info.line_width / 2
                    self.routing_info.last_direction = SceneDirection.Down
                self.routing_info.start_y = event_y
            point_list = self.get_points(x, y, width, height)
            pg = Polygon.create_polygon_by_layer_id(point_list, self.routing_info.layer_id)
            routing_item = pg.get_graphics_item(self.paintbrush_manage)
            pg.net_name = self.routing_info.net_name
            pg.net_location = self.layout_app.config.on_grid_value_floor(
                x + width / 2), self.layout_app.config.on_grid_value_floor(-(y + height / 2))
            net_item = pg.get_text_item(self.paintbrush_manage)
            routing_item.net_item = net_item
            self.addItem(net_item)
            if self.routing_info.is_add_net_text:
                text_layer_id = self.layout_app.config.met_to_net_map.get(pg.layer_id, '')
                if text_layer_id:
                    split_items = text_layer_id.split('-')
                    label = Label(int(split_items[0]), int(split_items[1]), pg.net_name, *pg.net_location)
                    text_item = label.get_graphics_item(self.paintbrush_manage)
                    self.addItem(text_item)
                    if text_item.layer_id not in self.label_obj_container:
                        self.label_obj_container[text_item.layer_id] = []
                    self.label_obj_container[text_item.layer_id].append(text_item)
                    self.path_label_list.append(text_item)
            self.addItem(routing_item)
            self.path_polygon_list.append(routing_item)
            routing_item.layer_id = self.routing_info.layer_id
            routing_item.net_name = self.routing_info.net_name
            routing_item.point_list = point_list
            if routing_item.layer_id not in self.polygon_obj_container:
                self.polygon_obj_container[self.routing_info.layer_id] = []
            self.polygon_obj_container[routing_item.layer_id].append(routing_item)
            if routing_item.net_name not in self.polygon_net_container:
                self.polygon_net_container[routing_item.net_name] = []
            self.polygon_net_container[routing_item.net_name].append(routing_item)
            if self.last_routing_item:
                if self.layout_app.config.is_adjacent_metal(self.last_routing_item.layer_id, routing_item.layer_id):
                    via_bb_list, via_layer_id = self.layout_app.get_via_bb_list(
                        self.last_routing_item.polygon_instance, routing_item.polygon_instance)
                    if via_bb_list and via_layer_id:
                        self.add_via_to_scene(via_bb_list, via_layer_id)
                self.first_routing_item = None
            self.last_routing_item = routing_item
            if self.first_routing_item:
                if self.layout_app.config.is_adjacent_metal(self.first_routing_item.layer_id, routing_item.layer_id):
                    via_bb_list, via_layer_id = self.layout_app.get_via_bb_list(
                        self.first_routing_item.polygon_instance, routing_item.polygon_instance)
                    if via_bb_list and via_layer_id:
                        self.add_via_to_scene(via_bb_list, via_layer_id)
                self.first_routing_item = None

    def handle_pre_add_polygon_left_button_press_event(self, event):
        if self.highlight_item and self.highlight_item.isVisible():
            self.mode = SceneMode.AddPath
            start_x = self.highlight_item.boundingRect().x() + self.highlight_item.boundingRect().width() / 2
            x = self.layout_app.config.on_grid_value_floor(int(event.scenePos().x()))
            y = self.layout_app.config.on_grid_value_floor(int(event.scenePos().y()))
            self.routing_info.set_start_position(x, y)
            self.removeItem(self.highlight_item)
            self.highlight_item = None
            pen, brush = self.paintbrush_manage.get_paintbrush(self.routing_info.layer_id)
            self.routing_item = self.addRect(start_x, event.scenePos().y(), 1, 1, pen, brush)

    def get_all_layer_id(self):
        all_layer_id_list = list(self.polygon_obj_container.keys())+list(self.label_obj_container.keys())
        all_layer_id_list.sort(key=lambda x: int(x.replace('-', '')))
        return all_layer_id_list

    def handle_left_button_press_event(self, event):

        item = self.itemAt(event.scenePos(), QTransform())
        if item and item not in self.selected_item_list and item.is_edit:
            if self.selected_item_list and self.mode == SceneMode.Normal:
                for s_item in self.selected_item_list:
                    self.reset_item(s_item)
                self.selected_item_list.clear()
            if self.mode == SceneMode.EditVia:
                if hasattr(item, 'layer_id') and self.layout_app.config.is_metal(item.layer_id):
                    self.selected_item_list.append(item)
                else:
                    QMessageBox.information(self.layout_view, "Invalid polygons", "Please select metal layer!")
            else:
                self.selected_item_list.append(item)
            if item.type() in [LayoutType.Rectangle, LayoutType.Polygon]:
                pen, _ = self.paintbrush_manage.get_selected_paintbrush()
                item.setPen(pen)
            else:
                item.setDefaultTextColor(self.paintbrush_manage.get_select_text_color())
        elif not item:
            for item in self.selected_item_list:
                self.reset_item(item)
            self.selected_item_list.clear()

    def mousePressEvent(self, event):

        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.mode == SceneMode.PrePath:
                self.handle_pre_add_polygon_left_button_press_event(event)
            elif self.mode == SceneMode.AddPath:
                self.handle_path_left_button_press_event(event)
            else:
                self.handle_left_button_press_event(event)
            self.mouse_start_point = (event.scenePos().x(), event.scenePos().y())

        return super(LayoutScene, self).mousePressEvent(event)

    def reset_item(self, item):
        if item.type() == LayoutType.Rectangle or item.type() == LayoutType.Polygon:
            pen, brush = self.paintbrush_manage.get_paintbrush(item.layer_id)
            item.setPen(pen)
            item.setBrush(brush)
        else:
            item.setDefaultTextColor(self.paintbrush_manage.get_default_text_color())

    def add_via_to_scene(self, bb_list, layer_id):
        pg_list = Polygon.get_pg_list_by_bb_list(bb_list, layer_id)
        if layer_id not in self.polygon_obj_container:
            self.polygon_obj_container[layer_id] = []
        for pg in pg_list:
            item = pg.get_graphics_item(self.paintbrush_manage)
            self.path_polygon_list.append(item)
            self.addItem(item)
            self.polygon_obj_container[layer_id].append(item)

    def clear_selected_item_list(self):
        for item in self.selected_item_list:
            self.reset_item(item)
        self.selected_item_list.clear()

    def handle_edit_via_left_button_release_event(self, event):
        if len(self.selected_item_list) == 2:
            layer_id1 = self.selected_item_list[0].layer_id
            layer_id2 = self.selected_item_list[1].layer_id
            if self.layout_app.is_metal(layer_id1) and self.layout_app.is_metal(layer_id2):
                if layer_id1 == layer_id2:
                    self.clear_selected_item_list()
                    QMessageBox.information(self.layout_view, "Invalid polygons", "Please select again!")
                else:
                    via_bb_list, via_layer_id = self.layout_app.get_via_bb_list(
                        self.selected_item_list[0].polygon_instance, self.selected_item_list[1].polygon_instance)
                    if via_bb_list:
                        self.clear_selected_item_list()
                        self.add_via_to_scene(via_bb_list, via_layer_id)
                    else:
                        self.clear_selected_item_list()
                        QMessageBox.information(self.layout_view, "Invalid polygons",
                                                "Area is too small to add via/cont !")

    def mouseReleaseEvent(self, event):
        if self.mode == SceneMode.EditVia:
            self.handle_edit_via_left_button_release_event(event)
        else:
            self.handle_swipe_to_select(event)
        self.mouse_start_point = None
        if self.select_rectangle_area_item:
            self.removeItem(self.select_rectangle_area_item)
            self.select_rectangle_area_item = None
        return super(LayoutScene, self).mouseReleaseEvent(event)

    def get_cell_polygons(self):
        polygon_list = []
        for polygon_item in self.path_polygon_list:
            polygon_list.append(polygon_item.polygon_instance)
        return polygon_list

    def get_cell_text(self):
        text_list = []
        for text_item in self.path_label_list:
            text_list.append(text_item.text_instance)
        return text_list

    def create_components_bb_polygon(self):
        pen, _ = self.paintbrush_manage.get_component_bb_paintbrush()
        for component in self.layout_app.top_layout_cell.references:
            bb = component.bb
            lines = [
                [bb[0], bb[1], bb[0], bb[3]],
                [bb[0], bb[3], bb[2], bb[3]],
                [bb[2], bb[3], bb[2], bb[1]],
                [bb[0], bb[1], bb[2], bb[1]],
            ]
            self.component_bb_container[component.name] = []
            for line in lines:
                line_item = LayoutLineItem(line[0], -line[1], line[2], -line[3])
                line_item.is_bbox = True
                line_item.setPen(pen)
                self.addItem(line_item)
                self.component_bb_container[component.name].append(line_item)

    def create_components_name_text(self):
        pen, _ = self.paintbrush_manage.get_component_name_paintbrush()
        for component in self.layout_app.top_layout_cell.references:
            if component.name.endswith('_ip'):
                c_name = re.sub("_\d+_ip", '', component.name)
            else:
                c_name = component.name
            font = self.paintbrush_manage.get_text_font(2000)
            text_item = LayoutTextItem(c_name)
            text_item.setFont(font)
            x = (component.bb[2]+component.bb[0])/2
            y = (component.bb[3]+component.bb[1])/2
            text_item.setPos(x - text_item.boundingRect().width() / 2, -y)
            self.addItem(text_item)
            self.component_name_container[component.name] = [text_item]

    def create_layout_polygon(self):

        x_list = []
        y_list = []
        all_layout_cell = [self.layout_app.top_layout_cell] + self.layout_app.top_layout_cell.references
        for cell in all_layout_cell:
            is_edit = True
            if cell != self.layout_app.top_layout_cell:
                is_edit = False
            for layer_id, pg_list in cell.polygon_data.items():
                if layer_id == forbidden_layer_id:
                    continue
                if layer_id not in self.polygon_obj_container:
                    self.polygon_obj_container[layer_id] = []
                for pg in pg_list:
                    item = pg.get_graphics_item(self.paintbrush_manage)
                    item.is_edit = is_edit
                    if self.show_mode == ShowMode.Simple:
                        item.hide()
                    self.addItem(item)
                    if item.polygon_instance.is_polygon:
                        for point in item.polygon_instance.point_list:
                            x_list.append(point[0])
                            y_list.append(-point[1])
                    else:
                        x_list.extend([pg.bb[0], pg.bb[2]])
                        y_list.extend([-pg.bb[1], -pg.bb[3]])

                    self.polygon_obj_container[layer_id].append(item)
                    if pg.net_name:
                        if pg.net_name not in self.polygon_net_container:
                            self.polygon_net_container[pg.net_name] = []
                        self.polygon_net_container[pg.net_name].append(item)
                        if cell != self.layout_app.top_layout_cell:
                            txt_item = pg.get_text_item(
                                self.paintbrush_manage, font_size=2000)
                        else:
                            txt_item = pg.get_text_item(
                                self.paintbrush_manage)
                        self.addItem(txt_item)
                        txt_item.hide()
                        item.net_item = txt_item
        min_x = min(x_list)
        min_y = min(y_list)
        max_x = max(x_list)
        max_y = max(y_list)
        width = max_x - min_x
        height = max_y - min_y
        self.bb = [min_x, min_y, max_x, max_y]
        self.width()
        self.height()
        self.setSceneRect(min_x - width, min_y - height, width * 3, height * 3)
        return

    def move_all_items(self, shift_x, shift_y):
        for item in self.items():
            x, y = item.pos().x(), item.pos().y()
            x += shift_x
            y += shift_y
            item.setPos(x, y)

    def show_label_by_name(self, net_name):
        pen, brush = self.paintbrush_manage.get_highlight_net_paintbrush(net_name)
        for item in self.polygon_net_container.get(net_name, []):
            item.setPen(pen)
            item.setBrush(brush)
            item.is_show_net = True
            item.show_net()

    def hide_label_by_name(self, net_name):
        for item in self.polygon_net_container.get(net_name, []):
            pen, brush = self.paintbrush_manage.get_paintbrush(item.layer_id)
            item.setPen(pen)
            item.setBrush(brush)
            item.is_show_net = False
            item.hide_net()

    def show_label_by_layer_id(self, layer_id):
        for obj in self.label_obj_container.get(layer_id, []):
            if not obj.is_delete():
                obj.show()

    def hide_label_by_layer_id(self, layer_id):
        for obj in self.label_obj_container.get(layer_id, []):
            obj.hide()

    def show_layer_polygon(self, layer_id):
        for obj in self.polygon_obj_container.get(layer_id, []):
            if not obj.is_delete():
                obj.show()

    def show_component_bb(self):
        for item_list in self.component_bb_container.values():
            for item in item_list:
                item.show()

    def hide_component_bb(self):
        for item_list in self.component_bb_container.values():
            for item in item_list:
                item.hide()

    def show_component_name_text(self):
        for item_list in self.component_name_container.values():
            for item in item_list:
                item.show()

    def hide_component_name_text(self):
        for item_list in self.component_name_container.values():
            for item in item_list:
                item.hide()

    def hide_layer_polygon(self, layer_id):
        for obj in self.polygon_obj_container.get(layer_id, []):
            obj.hide()

    def update_bounding_rect(self):

        for item_list in self.polygon_obj_container.values():
            for item in item_list:
                item.prepareGeometryChange()
                item.boundingRect()

    def create_text_label(self):
        all_layout_cell = [self.layout_app.top_layout_cell] + \
                          self.layout_app.top_layout_cell.references
        net_layer_id_set = set(list(self.layout_app.config.met_to_net_map.values()))
        for cell in all_layout_cell:
            is_edit = True
            if cell != self.layout_app.top_layout_cell:
                is_edit = False
            for layer_id, label_list in cell.label_data.items():
                if layer_id not in self.label_obj_container:
                    self.label_obj_container[layer_id] = []
                for label in label_list:
                    if layer_id == terminal_layer_id:
                        item = label.get_graphics_item(self.paintbrush_manage, font_size=1000)
                    elif cell != self.layout_app.top_layout_cell:
                        item = label.get_graphics_item(self.paintbrush_manage, font_size=2000)
                    else:
                        item = label.get_graphics_item(self.paintbrush_manage)
                    item.is_edit = is_edit
                    if self.show_mode == ShowMode.Simple:
                        item.hide()
                    self.addItem(item)
                    self.label_obj_container[layer_id].append(item)
                    if layer_id in net_layer_id_set:
                        if layer_id not in self.net_label_obj_container:
                            self.net_label_obj_container[layer_id] = []
                        self.net_label_obj_container[layer_id].append(item)
