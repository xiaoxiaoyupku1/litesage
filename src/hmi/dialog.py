import re
from PySide6.QtCore import (
    QStringListModel, Qt
)
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, 
    QDialogButtonBox, QVBoxLayout, QGridLayout,
    QFileDialog, QListView, QLabel
)
from src.tool.num import EngNum


class ParameterDialog(QDialog):
    def __init__(self, parent=None, item=None, limits=None):
        super().__init__(parent)
        self.setWindowTitle('Enter Parameters')
        formLayout = QFormLayout()
        text = item.toPlainText()
        parameters = re.split('\s+', text.strip())
        self.name = QLineEdit(parameters.pop(0))
        formLayout.addRow('Name:', self.name)
        self.devName = QLineEdit(parameters.pop(0))
        self.devName.setReadOnly(True)
        self.devName.setFrame(False)
        formLayout.addRow('Device:', self.devName)
        self.values = [] # list of (pname, QLineEdit)
        for param in parameters:
            if '=' in param:
                pname, value = param.split('=')
                value_qle = QLineEdit(value)
                formLayout.addRow(pname + ':', value_qle)
                self.values.append([pname, value_qle])
            else:
                value_qle = QLineEdit(param)
                formLayout.addRow('Param:', value_qle)
                self.values.append(['', value_qle])

        self.errMsg = QLabel()
        self.errMsg.setStyleSheet("color: red;")
        self.errMsg.hide()
        QBtn = QDialogButtonBox()
        QBtn.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        QBtn.accepted.connect(self.accept)
        QBtn.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addWidget(self.errMsg)
        layout.addWidget(QBtn)
        self.setLayout(layout)
        self.limits = limits

    def accept(self):
        for idx, (value, limit) in enumerate(zip(self.values, self.limits)):
            name, nom = value[0], limit[0]
            minVal, maxVal = limit[1:]
            if len(name) == 0 and minVal is None and maxVal is None:
                continue
            num = value[1].text().strip()
            try:
                num = EngNum(num)
            except:
                self.errMsg.setText('invalid input: {}={}'.format(name, num)) 
                self.errMsg.show()
                return
            if minVal is not None and num < minVal:
                self.errMsg.setText('invalid input: {}={}\nhint: \u2265 {}'.format(name, num, minVal))
                self.errMsg.show()
                return
            if maxVal is not None and num > maxVal:
                self.errMsg.setText('invalid input: {}={}\nhint: \u2264 {}'.format(name, num, maxVal))
                self.errMsg.show()
                return
            self.values[idx][1].setText(str(num))
        super().accept()



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
        self.thumbnailScene.mouseDoubleClickEvent = self._skip
        self.thumbnailScene.keyPressEvent = self._skip
        if self.symbType == 'pdk':
            self.thumbnailScene.initPdkDevices()
        elif self.symbType == 'ip':
            self.thumbnailScene.initIpDevices()
        self.thumbnailScene.gridOn = False
        self.thumbnailScene.isThumbnail = True
        self.thumbnailView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumbnailView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumbnailView.wheelEvent = self._skip
        self.thumbnailScene.update()