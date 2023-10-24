from src.layout.layout_ui import Ui_MainWindow
from PySide6 import QtWidgets
from src.layout.layout_scene import LayoutScene
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt, QIntValidator
from src.layout.layout_application import LayoutApplication
from PySide6.QtWidgets import QDialog
from src.layout.add_polygon import Ui_Dialog
from PySide6.QtGui import QTransform
import shutil
import os


class LayoutMode(object):

    Normal = 'Normal'
    Edit = 'Edit'
    Measure = 'Measure'
    AddPolygon = 'AddPolygon'


class LayoutMainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout_app = LayoutApplication()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.layout_scene = LayoutScene(self.layout_app, self.ui.graphicsView, self)
        self.ui.graphicsView.setScene(self.layout_scene)
        self.ui.graphicsView.layout_scene = self.layout_scene
        self.net_list_view_model = QStandardItemModel()
        self.layer_list_view_model = QStandardItemModel()
        self.mode = LayoutMode.Normal
        self.routing_dialog = QDialog(self)
        self.routing_dialog_ui = Ui_Dialog()
        self.routing_dialog_ui.setupUi(self.routing_dialog)
        self.setup()

    def update_layer_list_view(self):
        item = QStandardItem('all')
        self.layer_list_view_model.appendRow(item)
        item.setCheckable(True)
        for layer_id in self.layout_scene.get_all_layer_id():
            item = QStandardItem(layer_id)
            self.layer_list_view_model.appendRow(item)
            item.setCheckable(True)

    def add_polygon_accepted(self):
        net_name = self.routing_dialog_ui.lineEditNetName.text()
        layer_id = self.routing_dialog_ui.lineEditLayId.text()
        line_width = self.routing_dialog_ui.lineEditLineWidth.text()
        is_add_net_text = self.routing_dialog_ui.radioButton_yes.isChecked()
        if not line_width:
            QtWidgets.QMessageBox.information(self, "invalid input", "please input line width!")
        elif not layer_id or not self.layout_app.config.is_metal(layer_id):
            QtWidgets.QMessageBox.information(self, "invalid input", "please input metal id!")
        elif not net_name:
            QtWidgets.QMessageBox.information(self, "invalid input", "please select net name!")
        else:
            self.layout_scene.add_layout_polygon(net_name, layer_id, int(line_width), is_add_net_text)
            self.routing_dialog.close()

    def reset_view_model(self):
        self.net_list_view_model.clear()
        self.layer_list_view_model.clear()

    def key_press_p(self, *args):

        layer_id = ''
        net_name = ''
        routing_width = self.layout_app.config.routing_width if self.layout_app.config.routing_width else ''
        if self.ui.listViewLayers.selectedIndexes():
            ui_layer_id = self.layer_list_view_model.item(self.ui.listViewLayers.selectedIndexes()[0].row()).text()
            if ui_layer_id and self.layout_app.config.is_metal(ui_layer_id):
                layer_id = ui_layer_id
        if self.ui.listViewNets.selectedIndexes():
            net_name = self.net_list_view_model.item(self.ui.listViewNets.selectedIndexes()[0].row()).text()
        self.routing_dialog_ui.lineEditLineWidth.setText(str(routing_width))
        self.routing_dialog_ui.lineEditLayId.setText(layer_id)
        self.routing_dialog_ui.lineEditNetName.setText(net_name)
        self.routing_dialog.show()
        self.mode = LayoutMode.AddPolygon

    def keyPressEvent(self, event):

        if hasattr(self, "key_press_{}".format(event.text())):
            exec('self.key_press_{}(event)'.format(event.text()))
        elif hasattr(self, "key_press_uppercase_{}".format(event.text().lower())):
            exec('self.key_press_uppercase_{}(event)'.format(event.text().lower()))

        return super(LayoutMainWindow, self).keyPressEvent(event)

    def update_net_list_view(self):
        item = QStandardItem('all')
        self.net_list_view_model.appendRow(item)
        item.setCheckable(True)
        for net_name in self.layout_scene.get_net_name_list():
            item = QStandardItem(net_name)
            self.net_list_view_model.appendRow(item)
            item.setCheckable(True)

    def update_list_view(self):
        self.update_layer_list_view()
        self.update_net_list_view()

    def show_detail_canvas(self):
        self.layout_scene.create_layout_polygon()
        self.layout_scene.create_text_label()

    def show_simple_canvas(self):
        self.layout_scene.create_components_bb_polygon()
        self.layout_scene.create_components_name_text()

    def net_diffusion(self):
        for metal_layer_id, txt_layer_id in self.layout_app.config.met_to_net_map.items():
            if metal_layer_id in self.layout_app.gds_manage.polygon_data and txt_layer_id in \
                    self.layout_app.gds_manage.label_data:
                for pg in self.layout_app.gds_manage.polygon_data[metal_layer_id]:
                    pg_item = pg.get_temp_graphics_item(self.layout_scene.paintbrush_manage)
                    self.layout_scene.addItem(pg_item)
                for label in self.layout_app.gds_manage.label_data[txt_layer_id]:
                    item = self.layout_scene.itemAt(label.x, -label.y, QTransform())
                    if item:
                        item.polygon_instance.net_name = label.text
                        item.polygon_instance.net_location = label.x, label.y
                self.layout_scene.clear()

    def open_gds(self, file_path):
        if not file_path:
            file_path = QtWidgets.QFileDialog.getOpenFileName(self)[0]
        if file_path:
            self.reset_view_model()
            self.layout_scene.reset()
            self.layout_app.open_gds(file_path)
            self.net_diffusion()
            self.show_detail_canvas()
            self.show_simple_canvas()
            self.update_list_view()
            self.update_net_list_view()
            self.select_all_model_item(self.layer_list_view_model)
            self.ui.graphicsView.center_display()
            return

    def on_clicked_net_list_view(self, item):
        select_item = self.net_list_view_model.item(item.row(), item.column())
        if select_item.text() == 'all':
            if select_item.checkState() == Qt.CheckState.Checked:
                for row in range(self.net_list_view_model.rowCount()):
                    if row != 0:
                        self.net_list_view_model.item(row, 0).setCheckState(Qt.CheckState.Checked)
                        self.layout_scene.show_label_by_name(self.net_list_view_model.item(row, 0).text())
            else:
                for row in range(self.net_list_view_model.rowCount()):
                    if row != 0:
                        self.net_list_view_model.item(row, 0).setCheckState(Qt.CheckState.Unchecked)
                        self.layout_scene.hide_label_by_name(self.net_list_view_model.item(row, 0).text())
        else:
            if select_item.checkState() == Qt.CheckState.Checked:
                self.layout_scene.show_label_by_name(select_item.text())
            else:
                self.layout_scene.hide_label_by_name(select_item.text())
            if self.routing_dialog.isVisible():
                if self.ui.listViewNets.selectedIndexes():
                    net_name = self.net_list_view_model.item(self.ui.listViewNets.selectedIndexes()[0].row()).text()
                    if net_name != 'all':
                        self.routing_dialog_ui.lineEditNetName.setText(net_name)

    @staticmethod
    def select_all_model_item(model):
        for row in range(model.rowCount()):
            model.item(row, 0).setCheckState(Qt.CheckState.Checked)

    def refresh_layer_list_view(self):
        selected_layer_id_list = self.get_selected_layer_id_list()
        all_layer_id_list = self.layout_scene.get_all_layer_id()
        self.layer_list_view_model.clear()
        item = QStandardItem('all')
        self.layer_list_view_model.appendRow(item)
        item.setCheckState(Qt.CheckState.Unchecked)
        item.setCheckable(True)
        for layer_id in all_layer_id_list:
            item = QStandardItem(layer_id)
            item.setCheckable(True)
            self.layer_list_view_model.appendRow(item)
            if layer_id in selected_layer_id_list:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

    @staticmethod
    def hide_all_model_item(model):
        for row in range(model.rowCount()):
            model.item(row, 0).setCheckState(Qt.CheckState.Unchecked)

    def get_selected_layer_id_list(self):
        selected_layer_id_list = []
        for row in range(self.layer_list_view_model.rowCount()):
            select_item = self.layer_list_view_model.item(row, 0)
            if select_item.text() != 'all' and select_item.checkState() == Qt.CheckState.Checked:
                selected_layer_id_list.append(select_item.text())

        return selected_layer_id_list

    def on_clicked_layer_list_view(self, item):
        select_item = self.layer_list_view_model.item(item.row(), item.column())
        if select_item.text() == 'all':
            if select_item.checkState() == Qt.CheckState.Checked:
                for row in range(self.layer_list_view_model.rowCount()):
                    if row != 0:
                        self.layer_list_view_model.item(row, 0).setCheckState(Qt.CheckState.Checked)
                        self.layout_scene.show_layer_polygon(self.layer_list_view_model.item(row, 0).text())
                        self.layout_scene.show_label_by_layer_id(self.layer_list_view_model.item(row, 0).text())
            else:
                for row in range(self.layer_list_view_model.rowCount()):
                    if row != 0:
                        self.layer_list_view_model.item(row, 0).setCheckState(Qt.CheckState.Unchecked)
                        self.layout_scene.hide_layer_polygon(self.layer_list_view_model.item(row, 0).text())
                        self.layout_scene.hide_label_by_layer_id(self.layer_list_view_model.item(row, 0).text())
        else:
            if select_item.checkState() == Qt.CheckState.Checked:
                self.layout_scene.show_layer_polygon(select_item.text())
                self.layout_scene.show_label_by_layer_id(select_item.text())
            else:
                self.layout_scene.hide_layer_polygon(select_item.text())
                self.layout_scene.hide_label_by_layer_id(select_item.text())
            if self.routing_dialog.isVisible():
                if self.ui.listViewLayers.selectedIndexes():
                    layer_id = self.layer_list_view_model.item(self.ui.listViewLayers.selectedIndexes()[0].row()).text()
                    if layer_id != 'all' and self.layout_app.config.is_metal(layer_id):
                        self.routing_dialog_ui.lineEditLayId.setText(layer_id)

    @staticmethod
    def copy_file(source_file, destination_file):
        shutil.copyfile(source_file, destination_file)

    def save(self):
        polygon_list = self.layout_scene.get_cell_polygons()
        text_list = self.layout_scene.get_cell_text()
        self.layout_scene.clear_routing_polygons()
        self.layout_app.save_data(polygon_list, text_list)
        source_file, destination_file = self.layout_app.gds_manage.gds_path, self.layout_app.gds_manage.gds_path+'.bak'
        self.copy_file(source_file, destination_file)
        res, title, err_msg = self.layout_app.save_gds(self.layout_app.gds_manage.gds_path)
        if not res:
            if os.path.exists(destination_file):
                self.copy_file(destination_file, source_file)
                os.remove(destination_file)
            QtWidgets.QMessageBox.information(self, title, err_msg)
            return
        else:
            os.remove(destination_file)
            QtWidgets.QMessageBox.information(self, 'save info', 'save success!')

    def save_as(self, file_path=''):
        show_info = False
        if not file_path:
            show_info = True
            file_tuple = QtWidgets.QFileDialog.getSaveFileName(self, filter='.gds')
            file_path = file_tuple[0]
            if not file_path:
                return
            file_path += file_tuple[1]
        if file_path:
            polygon_list = self.layout_scene.get_cell_polygons()
            text_list = self.layout_scene.get_cell_text()
            self.layout_app.save_data(polygon_list, text_list)
            res, title, err_msg = self.layout_app.save_gds(file_path)
            if not res:
                if os.path.exists(file_path):
                    os.remove(file_path)
                if show_info:
                    QtWidgets.QMessageBox.information(self, title, err_msg)
                return
            if show_info:
                QtWidgets.QMessageBox.information(self, 'save info', 'save success!')

    def show_window_and_open_gds(self, file_path):
        self.show()
        self.open_gds(file_path)

    def setup_routing_dialog_ui(self):
        self.routing_dialog_ui.pushButtonConfirm.clicked.connect(self.add_polygon_accepted)
        self.routing_dialog_ui.pushButtonCancel.clicked.connect(lambda: self.routing_dialog.close())
        self.routing_dialog_ui.lineEditLineWidth.setValidator(QIntValidator())
        self.routing_dialog_ui.pushButtonConfirm.setShortcut(Qt.Key.Key_Enter)
        self.routing_dialog.setWindowTitle("routing params input")
        self.routing_dialog_ui.radioButton_yes.setChecked(True)

    def upload_gds(self):
        from src.tool.network import Gateway
        try:
            gt = Gateway()
            local_path = './project/layout/{}.metal.gds'.format(self.layout_app.top_layout_cell.name)
            remote_path = '/F/LaGen/gdsS2/{}.metal.gds'.format(self.layout_app.top_layout_cell.name)
            self.save_as(local_path)
            gt.uploadFile(local_path, remote_path)
            QtWidgets.QMessageBox.information(self, 'Upload info', 'upload success')
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.information(self, 'Upload info', 'upload Fail!')

    def setup(self):
        self.setup_routing_dialog_ui()
        self.ui.actionOpen.triggered.connect(self.open_gds)
        self.ui.listViewLayers.clicked.connect(self.on_clicked_layer_list_view)
        self.ui.listViewNets.clicked.connect(self.on_clicked_net_list_view)
        self.ui.listViewNets.setModel(self.net_list_view_model)
        self.ui.listViewLayers.setModel(self.layer_list_view_model)
        self.ui.listViewNets.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.listViewLayers.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionSave_As.triggered.connect(self.save_as)
        self.ui.actionExport.triggered.connect(self.save_as)
        self.ui.actionClose.triggered.connect(self.hide)
        self.ui.actionPath.triggered.connect(self.key_press_p)
        self.ui.actionVia.triggered.connect(self.layout_scene.key_press_o)
        self.ui.actionDele.triggered.connect(self.layout_scene.key_press_delete)
        self.ui.actionUpload.triggered.connect(self.upload_gds)
