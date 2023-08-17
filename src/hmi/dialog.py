import re
import os
from PySide6.QtCore import (
    QStringListModel, Qt
)
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, 
    QDialogButtonBox, QVBoxLayout, QGridLayout,
    QFileDialog, QListView, QLabel, QTabWidget
)
from src.hmi.text import NetlistText
from src.tool.num import EngNum


class DesignDialog(QDialog):
    def __init__(self, parent=None, designRect=None):
        super().__init__(parent)
        self.designRect = designRect
        if self.designRect.design.readonly:
            self.setWindowTitle('Enter Name:')
            layout = QVBoxLayout()
            formLayout = QFormLayout()
            self.name = QLineEdit(self.designRect.design.name)
            formLayout.addRow('Name:', self.name)
            layout.addLayout(formLayout)
        else:
            self.setWindowTitle('Enter Model Name:')
            layout = QVBoxLayout()
            formLayout = QFormLayout()
            self.model = QLineEdit(self.designRect.design.model)
            formLayout.addRow('Model Name:', self.model)
            layout.addLayout(formLayout)

        btn = QDialogButtonBox()
        btn.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)

        self.setLayout(layout)

    def accept(self) -> None:
        if self.designRect.design.readonly:
            self.designRect.design.name = self.name.text()
        else:
            self.designRect.design.model = self.model.text()
        super().accept()


class WireDialog(QDialog):
    def __init__(self, parent=None, wiresegment=None):
        super().__init__(parent)
        self.wiresegment = wiresegment
        self.setWindowTitle('Enter Wire Name')

        layout = QVBoxLayout()
        formLayout = QFormLayout()
        self.name = QLineEdit(self.wiresegment.wire.name)
        formLayout.addRow('Name:', self.name)
        layout.addLayout(formLayout)

        self.errMsg = QLabel()
        self.errMsg.setStyleSheet("color: red;")
        self.errMsg.hide()
        layout.addWidget(self.errMsg)

        btn = QDialogButtonBox()
        btn.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)

        self.setLayout(layout)

    def accept(self):
        for wire in self.wiresegment.scene().wireList:
            if wire is self.wiresegment.wire: #same wire
                continue
            if any(pin in self.wiresegment.wire.getPins() for pin in wire.getPins()):
                #the two wires linked to same pin
                if wire.name is not None:
                    if self.name.text() != wire.name:
                        self.errMsg.setText("Wires linked to same pin requied same name")
                        self.errMsg.show()
                        return
        super().accept()


class ParameterDialog(QDialog):
    def __init__(self, parent=None, item=None, params=None):
        super().__init__(parent)
        self.setWindowTitle('Enter Parameters')
        formLayout = QFormLayout()
        text = item.toPlainText()
        paramTextLines = re.split('\s+', text.strip())
        self.name = QLineEdit(paramTextLines.pop(0))
        formLayout.addRow('Name:', self.name)
        self.devName = QLineEdit(paramTextLines.pop(0))
        self.devName.setReadOnly(True)
        self.devName.setFrame(False)
        formLayout.addRow('Device:', self.devName)
        self.values = [] # list of (pname, QLineEdit)
        for param in params:
            name, prompt, value = param.name, param.prompt, param.value
            widget = QLineEdit(value)
            formLayout.addRow(prompt + ':', widget)
            self.values.append([name, widget])

        self.scale_percentage = QLineEdit(str(item.parentItem().scale()*100))
        formLayout.addRow("Scale(%):", self.scale_percentage)

        self.errMsg = QLabel()
        self.errMsg.setStyleSheet("color: red;")
        self.errMsg.hide()
        btn = QDialogButtonBox()
        btn.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addWidget(self.errMsg)
        layout.addWidget(btn)
        self.setLayout(layout)
        self.params = params

    def accept(self):
        for idx, (value, param) in enumerate(zip(self.values, self.params)):
            name = value[0]
            minVal, maxVal = param.minVal, param.maxVal
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
        directory = kwargs.get('directory')

        if not os.path.exists(directory):
            os.mkdir(directory)

        super().__init__(*args, **kwargs)
        self.accepted = QDialog.Accepted

        #filters=["Design Files (*.dsgn)",
        #         "Any files (*)"
        #         ]
        filters="Design Files (*.dsgn)"
        self.setNameFilter(filters)

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


class NetlistDialog(QDialog):
    def __init__(self, parent=None, netlist=[]):
        super().__init__(parent)
        self.setWindowTitle('SPICE Netlist')

        browser = NetlistText()
        browser.setText('\n'.join(netlist))

        btn = QDialogButtonBox()
        btn.setStandardButtons(QDialogButtonBox.Close)
        btn.rejected.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(browser)
        layout.addWidget(btn)
        self.setLayout(layout)


class SimulationCommandDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init()
        self.setup()

    def init(self):
        self.setWindowTitle('SPICE Analysis')
        self.setFixedSize(600, 300)
        self.accepted = QDialog.Accepted
        self.command = ''
        dialTran = SimCmdDialog_TRAN(self)
        dialAc = SimCmdDialog_AC(self)
        dialDc = SimCmdDialog_DC(self)
        dialDcOp = SimCmdDialog_DCOP(self)
        dialCustom = SimCmdDialog_CUSTOMIZE(self)
        self.dialogs = [dialTran, dialAc, dialDc, dialDcOp, dialCustom]
        self.dialNames = ['TRAN', 'AC', 'DC', 'DC OP', 'Customize']

    def setup(self):
        self.tab = QTabWidget(self)
        for dial, dialName in zip(self.dialogs, self.dialNames):
            self.tab.addTab(dial, dialName)

        btn = QDialogButtonBox()
        btn.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.tab)
        layout.addWidget(btn)
        self.setLayout(layout)

    def accept(self):
        tabId = self.tab.currentIndex()
        self.command = self.dialogs[tabId].getCommand()
        if len(self.command) == 0:
            self.reject()
        else:
            super().accept()

        
class SimCmdDialog_TRAN(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.start = QLineEdit('0')
        self.stop = QLineEdit('1m')
        self.step = QLineEdit('1n')
        layout.addRow('Start Time', self.start)
        layout.addRow('Stop Time', self.stop)
        layout.addRow('Increment', self.step)
        self.setLayout(layout)
    
    def getCommand(self):
        start = self.start.text().strip()
        start = '' if start == '0' else ' start={}'.format(start)
        stop = self.stop.text().strip()
        step = self.step.text().strip()
        return '.tran {} {}{}'.format(step, stop, start)

class SimCmdDialog_AC(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.sweep = QLineEdit('dec')
        self.num = QLineEdit('10')
        self.start = QLineEdit('1m')
        self.stop = QLineEdit('10meg')
        layout.addRow('Type of Sweep (dec, oct, lin)', self.sweep)
        layout.addRow('Number of Points', self.num)
        layout.addRow('Start', self.start)
        layout.addRow('Stop', self.stop)
        self.setLayout(layout)
    
    def getCommand(self):
        sweep = self.sweep.text().strip()
        num = self.num.text().strip()
        start = self.start.text().strip()
        stop = self.stop.text().strip()
        return '.ac {} {} {} {}'.format(sweep, num, start, stop)

class SimCmdDialog_DC(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.sweep = QLineEdit('temp')
        self.start = QLineEdit('-40')
        self.stop = QLineEdit('150')
        self.step = QLineEdit('1')
        layout.addRow('Sweep Variable', self.sweep)
        layout.addRow('Start', self.start)
        layout.addRow('Stop', self.stop)
        layout.addRow('Increment', self.step)
        self.setLayout(layout)
    
    def getCommand(self):
        sweep = self.sweep.text().strip()
        start = self.start.text().strip()
        stop = self.stop.text().strip()
        step = self.step.text().strip()
        return '.dc {} {} {} {}'.format(sweep, start, stop, step)

class SimCmdDialog_DCOP(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        label = QLabel()
        label.setText('Save DC Operating Point')
        layout.addRow('', label)
        self.setLayout(layout)

    def getCommand(self):
        return '.op'

class SimCmdDialog_CUSTOMIZE(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.text = QLineEdit('.option temp=25')
        layout.addRow('', self.text)
        self.setLayout(layout)

    def getCommand(self):
        return self.text.text().strip()