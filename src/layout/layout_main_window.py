from src.layout.layout_ui import Ui_MainWindow
from PySide6 import QtWidgets
from src.layout.layout_scene import LayoutScene
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from src.layout.layout_application import LayoutApplication


class LayoutMainWindow(QtWidgets.QMainWindow):

    def __init__(self, main_app, eda, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_app = main_app
        self.eda = eda
        self.layout_app = LayoutApplication()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.layout_scene = LayoutScene(self.layout_app, self.ui.graphicsView)
        self.ui.graphicsView.setScene(self.layout_scene)
        self.ui.graphicsView.layout_scene = self.layout_scene
        self.net_list_view_model = QStandardItemModel()
        self.layer_list_view_model = QStandardItemModel()
        self.setup()

    def update_layer_list_view(self):
        item = QStandardItem('all')
        self.layer_list_view_model.appendRow(item)
        item.setCheckable(True)
        for layer_id in self.layout_app.get_layer_list_view_data():
            item = QStandardItem(layer_id)
            self.layer_list_view_model.appendRow(item)
            item.setCheckable(True)

    def update_net_list_view(self):
        item = QStandardItem('all')
        self.net_list_view_model.appendRow(item)
        item.setCheckable(True)
        for net_name in self.layout_app.get_net_list_view_data():
            item = QStandardItem(net_name)
            self.net_list_view_model.appendRow(item)
            item.setCheckable(True)

    def update_list_view(self):
        self.update_layer_list_view()
        self.update_net_list_view()

    def show_detail_canvas(self):
        self.layout_scene.create_layout_polygon()
        self.layout_scene.create_net_label()
        self.ui.graphicsView.center_display()

    def open_gds(self):
        file_tuple = QtWidgets.QFileDialog.getOpenFileName()
        if file_tuple[0]:
            self.layout_app.load_gds(file_tuple[0])
            self.show_detail_canvas()
            self.update_list_view()
            self.select_all_model_item(self.layer_list_view_model)
            self.select_all_model_item(self.net_list_view_model)
            # self.ui.graphicsView.center_display()

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

    @staticmethod
    def select_all_model_item(model):
        for row in range(model.rowCount()):
            model.item(row, 0).setCheckState(Qt.CheckState.Checked)

    @staticmethod
    def hide_all_model_item(model):
        for row in range(model.rowCount()):
            model.item(row, 0).setCheckState(Qt.CheckState.Unchecked)

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

    def setup(self):
        self.ui.actionLoad.triggered.connect(self.open_gds)
        self.ui.listViewLayers.clicked.connect(self.on_clicked_layer_list_view)
        self.ui.listViewNets.clicked.connect(self.on_clicked_net_list_view)
        self.ui.listViewNets.setModel(self.net_list_view_model)
        self.ui.listViewLayers.setModel(self.layer_list_view_model)
        self.ui.listViewNets.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.listViewLayers.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
