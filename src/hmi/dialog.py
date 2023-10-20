import re
import os
from PySide6.QtCore import (
    QStringListModel, Qt
)
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton,
    QDialogButtonBox, QVBoxLayout, QGridLayout,
    QFileDialog, QListView, QLabel, QTabWidget, QCheckBox
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

            self.scale_percentage = QLineEdit(str(designRect.scale() * 100))
            formLayout.addRow("Scale(%):", self.scale_percentage)

            self.show = QCheckBox("Show Details")
            self.show.setCheckState(self.designRect.design.show)
            formLayout.addRow(self.show)

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
            self.designRect.design.updateInfo()
            self.designRect.design.setScale(float(self.scale_percentage.text())/100)
            if self.designRect.design.show != self.show.checkState():
                self.designRect.design.setShow(self.show.checkState())
        else:
            self.designRect.design.model = self.model.text()
            self.designRect.design.updateInfo()
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
        type = kwargs.pop('type', 'design')
        directory = kwargs.get('directory')

        if not os.path.exists(directory):
            os.mkdir(directory)

        super().__init__(*args, **kwargs)
        self.accepted = QDialog.Accepted

        if type == 'design':
            filters="Design Files (*.dsgn)"
        elif type == 'sch':
            filters = "Schematic Files (*.sch)"
        else:
            pass
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
        if self.devInfo is not None:
            prompt = self.devInfo[self.device].getPrompt()
        else:
            prompt = ''

        self.description.setText(prompt)
        self.thumbnailScene.clear()
        if self.symbType == 'design':
            self.thumbnailScene.drawDesign([0,0], self.device)
        else:
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
        elif self.symbType == 'design':
            self.thumbnailScene.initDesignDevices()
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
        self.setFixedSize(680, 510)

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
    def __init__(self, parent=None, text=''):
        super().__init__(parent)
        self.init()
        self.setup()
        self.parseText(text)

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

    def parseText(self, text):
        if len(text) == 0:
            return
        elif text.lower().startswith('.tran '):
            tabId = 0
        elif text.lower().startswith('.ac '):
            tabId = 1
        elif text.lower().startswith('.dc '):
            tabId = 2
        elif text.lower() == '.op':
            tabId = 3
        else:
            tabId = 4
        self.tab.setCurrentIndex(tabId)
        self.dialogs[tabId].setCommand(text)

        
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

    def setCommand(self, text):
        """
        Syntax: .TRAN <Tstep> <Tstop> [Tstart [dTmax]] [modifiers]
        .TRAN <Tstop> [modifiers]
        """ 
        items = text.split()
        length = len(items)

        if length == 1:
            return
        if length > 1:
            self.step.setText(items[1])
        if length > 2:
            self.stop.setText(items[2])
        if length > 3:
            self.start.setText(' '.join(items[3]))


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

    def setCommand(self, text):
        """
        Syntax: .ac <oct, dec, lin> <Nsteps> <StartFreq> <EndFreq>
        .ac list <FirstFreq> [<NextFreq> [<NextFreq> ...]]
        """
        items = text.split()
        length = len(items)

        if length == 1:
            return
        if length > 1:
            self.sweep.setText(items[1])
        if length > 2:
            self.num.setText(items[2])
        if length > 3:
            self.start.setText(items[3])
        if length > 4:
            self.stop.setText(' '.join(items[4:]))

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

    def setCommand(self, text):
        """
        Syntax: .dc <srcnam> <Vstart> <Vstop> <Vincr>
        + [<srcnam2> <Vstart2> <Vstop2> <Vincr2>]
        """
        items = text.split()
        length = len(items)

        if length == 1:
            return
        if length > 1:
            self.sweep.setText(items[1])
        if length > 2:
            self.start.setText(items[2])
        if length > 3:
            self.stop.setText(items[3])
        if length > 4:
            self.step.setText(' '.join(items[4:]))


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

    def setCommand(self, text):
        return

class SimCmdDialog_CUSTOMIZE(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.text = QLineEdit('.option temp=25')
        layout.addRow('', self.text)
        self.setLayout(layout)

    def getCommand(self):
        return self.text.text().strip()
    
    def setCommand(self, text):
        self.text.setText(text)


class UserAccountDialog(QDialog):
    def __init__(self, user, skip=False):
        self.user = user
        self.info = []
        super().__init__()
        self.setWindowTitle('User Account Sign Up/In')
        self.accepted = QDialog.Accepted

        form = QFormLayout()

        self.name = QLineEdit('')
        self.name.setText(self.user.name)
        self.name.setClearButtonEnabled(True)
        form.addRow('Name:', self.name)

        self.phone = QLineEdit('')
        self.phone.setText(self.user.phone)
        self.phone.setClearButtonEnabled(True)
        form.addRow('Phone:', self.phone)

        self.passwd = QLineEdit('')
        self.passwd.setText(self.user.passwd)
        self.passwd.setClearButtonEnabled(True)
        self.passwd.setEchoMode(QLineEdit.Password)
        form.addRow('Password:', self.passwd)

        self.org = QLineEdit('')
        self.org.setText(self.user.org)
        self.org.setClearButtonEnabled(True)
        form.addRow('Organization:', self.org)

        self.role = QLineEdit('')
        self.role.setText(self.user.role)
        self.role.setClearButtonEnabled(True)
        form.addRow('Role:', self.role)

        self.errMsg = QLabel()
        self.errMsg.setStyleSheet('color: red;')
        self.errMsg.hide()

        if skip:
            btn = QDialogButtonBox(QDialogButtonBox.Ok,)
            skipBtn = QPushButton('Skip', self)
            btn.addButton(skipBtn, QDialogButtonBox.RejectRole)
        else:
            btn = QDialogButtonBox()
            btn.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.close)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.errMsg)
        layout.addWidget(btn)
        self.setLayout(layout)

    def accept(self):
        name = self.name.text().strip()
        phone = self.phone.text().strip()
        passwd = self.passwd.text().strip()
        org = self.org.text().strip()
        role = self.role.text().strip()

        if len(name) == 0:
            self.errMsg.setText('empty user name')
            self.errMsg.show()
            return
        elif len(phone) != 11 or not phone.isnumeric():
            self.errMsg.setText('invalid phone number: {}'.format(phone))
            self.errMsg.show()
            return
        elif len(passwd) == 0:
            self.errMsg.setText('empty password')
            self.errMsg.show()
            return
        self.info = [name, phone, passwd, org, role]
        super().accept()


class Confirmation(QDialog):
    def __init__(self, warn: str):
        super().__init__()
        self.setWindowTitle("Alert:")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(warn)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)