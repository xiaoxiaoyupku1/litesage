from PySide6.QtCore import (QRect )
from PySide6.QtWidgets import (
    QMainWindow, QMenuBar, QMenu, QWidget, QGraphicsView
)
from PySide6.QtGui import (
    QAction, QIcon, QKeySequence
)

from src.waveform import FoohuEdaWaveWindow
from src.layout import runLayout
from src.hmi.scene import SchScene
from src.hmi.view import SchView
from src.hmi.dialog import DesignFileDialog, DeviceChoiceDialog
from src.tool.design import dumpDesign


class FoohuEda(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()
        self.setupUi()
        self.initSchScene()

    def initUi(self):
        # Windows
        # self = main window = schematic editor window
        self.wavWin = None
        self.layWin = None

        self.centralWidget = None   # widget to put view on
        self.schView = None         # view to put scene on
        self.schScene = None        # scene to put symbols on
        self.cursorSymb = None      # symbol to insert

        # Menus
        self.menuBar = None
        self.menuFile = None
        self.menuEdit = None
        self.menuWave = None
        self.menuLayout = None

        # Menu File
        self.actSave = None
        self.actLoad = None

        # Menu Edit
        self.actBasic = None
        self.actPdk = None
        self.actIp = None
        self.actRes = None
        self.actGnd = None
        self.actVsrc = None
        self.actWire = None
        self.actPin = None
        self.actRect = None
        self.actSim = None
        self.actFit = None
        self.actGrid = None
        self.actNetlist = None

        # Menu Wave
        self.actOpenWave = None

        # Menu Layout
        self.actOpenLayout = None


    def setupUi(self):
        if not self.objectName():
            self.setObjectName('Main')
        self.resize(800, 600)
        self.setWindowTitle('FOOHU EDA - Schematic Editor')
        self.cursorSymb = 'NA'

        self.setupUiAction()
        self.setupUiMenu()

    def setupUiAction(self):
        self.actSave = QAction(text='Save Design')
        self.actSave.triggered.connect(self.saveDesign)

        self.actLoad = QAction(text='Load Design')
        self.actLoad.triggered.connect(self.loadDesign)

        self.actBasic = QAction(text='Add Standard Component...')
        self.actBasic.setObjectName('actBasic')
        self.actBasic.setShortcut(QKeySequence('f2'))
        self.actBasic.triggered.connect(self.addBasicDev)

        self.actPdk = QAction(text='Add PDK Component...')
        self.actPdk.setObjectName('actPdk')
        self.actPdk.setShortcut(QKeySequence('f3'))
        self.actPdk.triggered.connect(self.addPdkDev)

        self.actIp = QAction(text='Add IP Component...')
        self.actIp.setObjectName('actIp')
        self.actIp.setShortcut(QKeySequence('f4'))
        self.actIp.triggered.connect(self.addIpDev)

        self.actRes = QAction(QIcon('img/res.png'), '&', self,
                              text='Resistor')
        self.actRes.setObjectName('actRes')
        self.actRes.setShortcut(QKeySequence('r'))
        self.actRes.triggered.connect(self.drawRes)

        self.actGnd = QAction(QIcon('img/gnd.png'), '&', self, 
                              text='Ground')
        self.actGnd.setObjectName('actGnd')
        self.actGnd.setShortcut(QKeySequence('g'))
        self.actGnd.triggered.connect(self.drawGnd)

        self.actVsrc = QAction(QIcon('img/vsrc.png'), '&', self, 
                               text='Voltage Source')
        self.actVsrc.setObjectName('actVsrc')
        self.actVsrc.setShortcut(QKeySequence('v'))
        self.actVsrc.triggered.connect(self.drawVsrc)

        self.actWire = QAction(QIcon('img/wire.png'), '&', self, 
                               text='Wire')
        self.actWire.setObjectName('actWire')
        self.actWire.setShortcut(QKeySequence('w'))
        self.actWire.triggered.connect(self.drawWire)

        self.actPin = QAction(QIcon('img/pin.png'), '&', self, 
                              text='Pin')
        self.actPin.setObjectName('actPin')
        self.actPin.setShortcut(QKeySequence('p'))
        self.actPin.triggered.connect(self.drawPin)

        self.actRect = QAction(QIcon('img/rect.png'), '&', self, 
                               text='Design Rectangle')
        self.actRect.setObjectName('actRect')
        self.actRect.setShortcut(QKeySequence('t'))
        self.actRect.triggered.connect(self.drawRect)

        self.actSim = QAction(QIcon('img/sim.png'), '&', self,
                              text='Simulation Command')
        self.actSim.setObjectName('actSim')
        self.actSim.setShortcut(QKeySequence('s'))
        self.actSim.triggered.connect(self.drawSim)

        self.actFit = QAction(text='Fit')
        self.actFit.setObjectName('actFit')
        self.actFit.setShortcut(QKeySequence('f'))
        self.actFit.triggered.connect(self.fit)

        self.actGrid = QAction(text='Turn On/Off Grid')
        self.actGrid.setObjectName('actGrid')
        self.actGrid.setShortcut(QKeySequence('ctrl+g'))
        self.actGrid.triggered.connect(self.toggleGrid)

        self.actNetlist = QAction(text='SPICE Netlist')
        self.actNetlist.setObjectName('actNetlist')
        self.actNetlist.setShortcut(QKeySequence('ctrl+n'))
        self.actNetlist.triggered.connect(self.showNetlist)

        self.actOpenWave = QAction(text='Open Wave')
        self.actOpenWave.triggered.connect(self.openWave)
        self.actOpenLayout = QAction(text='Open Layout')
        self.actOpenLayout.triggered.connect(self.openLayout)

    def setupUiMenu(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setTitle('File')
        self.menuFile.addAction(self.actSave)
        self.menuFile.addAction(self.actLoad)

        self.menuEdit = QMenu(self.menuBar)
        self.menuEdit.setTitle('Edit')

        self.menuEdit.addAction(self.actBasic)
        self.menuEdit.addAction(self.actPdk)
        self.menuEdit.addAction(self.actIp)
        self.menuEdit.addAction(self.actRes)
        # self.menuEdit.addAction(self.actGnd)
        self.menuEdit.addAction(self.actVsrc)
        self.menuEdit.addAction(self.actWire)
        self.menuEdit.addAction(self.actPin)
        self.menuEdit.addAction(self.actRect)
        self.menuEdit.addAction(self.actSim)
        self.menuEdit.addAction(self.actFit)
        self.menuEdit.addAction(self.actGrid) 
        self.menuEdit.addAction(self.actNetlist)

        self.menuWave = QMenu(self.menuBar)
        self.menuWave.setTitle('Wave')
        self.menuWave.addAction(self.actOpenWave)

        self.menuLayout = QMenu(self.menuBar)
        self.menuLayout.setTitle('Layout')
        self.menuLayout.addAction(self.actOpenLayout)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuWave.menuAction())
        self.menuBar.addAction(self.menuLayout.menuAction())

        self.centralWidget = QWidget(self)
        self.centralView = QGraphicsView(self.centralWidget)
        self.centralView.setGeometry(QRect(0, 0, 500, 500))
        self.setCentralWidget(self.centralWidget)

    def saveDesign(self, _):
        if self.schScene is None or self.schScene.rectDesign is None:
            return
        dialog = DesignFileDialog(self, 'Save Design as ...', mode='save')
        result = dialog.exec()
        if result != dialog.accepted:
            return False
        designFile = dialog.selectedFiles()[0]
        dumpDesign(designFile, self.schScene.rectDesign)

    def loadDesign(self, _):
        self.schScene.cleanCursorSymb()
        dialog = DesignFileDialog(self, 'Load Design from ...', mode='load')
        result = dialog.exec()
        if result != dialog.accepted:
            return False
        designFile = dialog.selectedFiles()[0]
        self.schScene.insertSymbType = 'Design'
        with open(designFile, 'r') as filePort:
            self.schScene.designTextLines = filePort.read().splitlines()

    def initSchScene(self):
        if self.schScene is None:
            self.schScene = SchScene()
            self.schView = SchView(self.schScene)
            self.setCentralWidget(self.schView)

    def addBasicDev(self):
        self.schScene.cleanCursorSymb()
        devices = sorted(self.schScene.basicSymbols.keys())
        devInfo = self.schScene.basicDevInfo
        dialog = DeviceChoiceDialog(self, 'Add Standard Component', 
                                    devices=devices, 
                                    devInfo=devInfo,
                                    symbType='basic')
        result = dialog.exec()
        if result != dialog.accepted:
            return False
        self.drawSymbol(dialog.device, 'basic')
    
    def addPdkDev(self):
        self.schScene.cleanCursorSymb()
        self.schScene.initPdkDevices()
        devices = sorted(self.schScene.pdkSymbols.keys())
        devInfo = self.schScene.pdkDevInfo
        dialog = DeviceChoiceDialog(self, 'Add PDK Component', 
                                    devices=devices,
                                    devInfo=devInfo,
                                    symbType='pdk')
        result = dialog.exec()
        if result != dialog.accepted:
            return False
        self.drawSymbol(dialog.device, 'pdk')

    def addIpDev(self):
        self.schScene.cleanCursorSymb()
        self.schScene.initIpDevices()
        devices = sorted(self.schScene.ipSymbols.keys())
        devInfo = self.schScene.ipDevInfo
        dialog = DeviceChoiceDialog(self, 'Add IP Component', 
                                    devices=devices,
                                    devInfo=devInfo,
                                    symbType='ip')
        result = dialog.exec()
        if result != dialog.accepted:
            return False
        self.drawSymbol(dialog.device, 'ip')
        
    def drawRes(self):
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'R'

    def drawVsrc(self):
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'V'

    def drawGnd(self):
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'G'

    def drawWire(self):
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'W'
        
    def drawPin(self):
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'P'
        
    def drawRect(self):
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'RECT'

    def drawSymbol(self, name, symbType):
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbName = name
        self.schScene.insertSymbType = symbType

    def drawSim(self):
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'S'

    def fit(self):
        self.schView.fit(self.schScene)

    def toggleGrid(self):
        self.schScene.toggleGrid()

    def showNetlist(self):
        self.schScene.showNetlist()

    def openWave(self):
        if self.wavWin is not None:
            self.wavWin.destroy()
        wavefile = 'examples/wave/waveform.tr0'
        self.wavWin = FoohuEdaWaveWindow(self, wavefile)

    def openLayout(self):
        gdsfile = 'examples/layout/reference.gds'
        runLayout(gdsfile)