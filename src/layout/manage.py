from src.layout.layout_ui import Ui_MainWindow
from PySide6 import QtWidgets
from src.layout.layout_scene import LayoutScene
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListView, QMessageBox
from PySide6.QtCore import QStringListModel


class LayoutApplication(QtWidgets.QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.layout_scene = LayoutScene()
        self.ui.graphicsView.setScene(self.layout_scene)

    def open(self):
        self.layout_scene.addRect(0,0,100,100)
        self.layout_scene.addRect(200,200,100,100)
        layer_listModel = QStringListModel()
        layer_list =['layer_{}'.format(str(i)) for i in range(100)]
        layer_listModel.setStringList(layer_list)
        net_listModel = QStringListModel()
        net_layer_list =['NET_{}'.format(str(i)) for i in range(100)]
        net_listModel.setStringList(net_layer_list)
        self.ui.listViewNets.setModel(net_listModel)
        self.ui.listViewLayers.setModel(layer_listModel)
        self.show()

