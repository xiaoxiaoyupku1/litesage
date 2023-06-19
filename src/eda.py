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
from src.hmi.dialog import DesignFileDialog
from src.tool.design import dumpDesign


class FoohuEda(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()
        self.setupUi()

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
        self.actRes = None
        self.actGnd = None
        self.actVsrc = None
        self.actWire = None
        self.actPin = None
        self.actRect = None
        self.actSim = None

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
        self.menuEdit.addAction(self.actRes)
        self.menuEdit.addAction(self.actGnd)
        self.menuEdit.addAction(self.actVsrc)
        self.menuEdit.addAction(self.actWire)
        self.menuEdit.addAction(self.actPin)
        self.menuEdit.addAction(self.actRect)
        self.menuEdit.addAction(self.actSim)

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
        if dialog.exec() != dialog.accepted:
            return False
        designFile = dialog.selectedFiles()[0]
        dumpDesign(designFile, self.schScene.rectDesign)

    def loadDesign(self, _):
        self.initSchScene()
        self.schScene.cleanCursorSymb()
        dialog = DesignFileDialog(self, 'Load Design from ...', mode='load')
        if dialog.exec() != dialog.accepted:
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

    def drawRes(self):
        self.initSchScene()
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'R'

    def drawVsrc(self):
        self.initSchScene()
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'V'

    def drawGnd(self):
        self.initSchScene()
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'G'

    def drawWire(self):
        self.initSchScene()
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'W'
        
    def drawPin(self):
        self.initSchScene()
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'P'
        
    def drawRect(self):
        self.initSchScene()
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'RECT'
        
    def drawSim(self):
        self.initSchScene()
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'S'

    def openWave(self):
        if self.wavWin is not None:
            self.wavWin.destroy()
        wavefile = 'examples/wave/waveform.tr0'
        self.wavWin = FoohuEdaWaveWindow(self, wavefile)

    def openLayout(self):
        gdsfile = 'examples/layout/reference.gds'
        runLayout(gdsfile)