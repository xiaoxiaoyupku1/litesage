import re
from PySide6.QtCore import (
    QStringListModel, Qt
)
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, 
    QDialogButtonBox, QVBoxLayout, QGridLayout,
    QFileDialog, QListView, QLabel, 
)


class ParameterDialog(QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle('Enter Paramters')
        formLayout = QFormLayout()
        text = item.toPlainText()
        currentName, currentValue = re.split('\s+', text.strip())
        self.name = QLineEdit(currentName)
        self.value = QLineEdit(currentValue)
        formLayout.addRow('Name:', self.name)
        formLayout.addRow('Value:', self.value)
        QBtn = QDialogButtonBox()
        QBtn.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        QBtn.accepted.connect(self.accept)
        QBtn.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addWidget(QBtn)
        self.setLayout(layout)


class DesignFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', 'load')       # load or save
        super().__init__(*args, **kwargs)
        self.accepted = QDialog.Accepted

        mimeTypes = ['text/plain']
        self.setMimeTypeFilters(mimeTypes)

        if mode == 'load':
            acceptMode = QFileDialog.AcceptOpen
        else:
            acceptMode = QFileDialog.AcceptSave
        self.setAcceptMode(acceptMode)


class DeviceChoiceDialog(QDialog):
    def __init__(self, parent, title, devices=[], devInfo={}, symbType='basic'):
        super().__init__(parent)
        self.setFixedSize(500, 400)
        self.device = None
        self.accepted = QDialog.Accepted
        self.setWindowTitle(title)
        self.devInfo = devInfo
        self.symbType = symbType

        # thumbnail
        from src.hmi.view import SchView
        from src.hmi.scene import SchScene
        self.thumbnailScene = SchScene()
        self.thumbnailView = SchView(self.thumbnailScene)
        self.formatThumbnail()
        self.thumbnailView.setFixedHeight(250)

        # description
        self.description = QLabel()
        self.description.setWordWrap(True)

        # list view
        strlist = QStringListModel()
        strlist.setStringList(devices)
        self.listview = QListView()
        self.listview.setModel(strlist)
        self.listview.pressed.connect(self.selDevice)
        self.listview.clicked.connect(self.selDevice)
        self.listview.entered.connect(self.selDevice)
        self.listview.doubleClicked.connect(self.accept)
        self.listview.setFixedWidth(160)

        # buttons
        btn = QDialogButtonBox()
        btn.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)

        # packing
        layout = QGridLayout()
        layout.addWidget(self.thumbnailView, 0, 1, 1, 1)
        layout.addWidget(self.description, 1, 1, 1, 1)
        layout.addWidget(self.listview, 0, 0, 2, 1)
        layout.addWidget(btn, 2, 0, 1, 2)
        self.setLayout(layout)

    def selDevice(self, event):
        self.device = event.data()
        prompt = self.devInfo[self.device].getPrompt()
        self.description.setText(prompt)
        self.thumbnailScene.clear()
        self.thumbnailScene.drawSymbol([0, 0], 
                                       self.device, 
                                       symbType=self.symbType)
        self.thumbnailView.fitInView(self.thumbnailScene.cursorSymb.boundingRect(),
                                     Qt.KeepAspectRatio)

    def _skip(self, _):
        pass
    def formatThumbnail(self):
        self.thumbnailScene.mouseMoveEvent = self._skip
        self.thumbnailScene.mousePressEvent = self._skip
        if self.symbType == 'pdk':
            self.thumbnailScene.initPdkDevices()
        elif self.symbType == 'ip':
            self.thumbnailScene.initIpDevices()
        self.thumbnailScene.gridOn = False
        self.thumbnailView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumbnailView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumbnailScene.update()