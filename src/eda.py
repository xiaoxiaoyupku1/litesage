from PySide6.QtCore import (QRect)
from PySide6.QtWidgets import (
    QMainWindow, QMenuBar, QMenu, QWidget, QGraphicsView, QMessageBox, 
    QLabel, QSizePolicy
)
from PySide6.QtGui import (
    QAction, QKeySequence
)

from src.hmi.scene import SchScene
from src.hmi.view import SchView
from src.hmi.dialog import DesignFileDialog, DeviceChoiceDialog, UserAccountDialog, Confirmation
from src.hmi.image import getIcon, getTrademark
from src.hmi.group import (SchInst, DesignGroup)
from src.hmi.rect import DesignBorder
from src.tool.status import setStatus
from src.tool.account import UserAccount
from src.tool.sys import readFile
from src.tool.config import PRODUCT_NAME
from src.waveform import WaveformViewer
from src.layout.layout_main_window import LayoutMainWindow


class FoohuEda(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.initUser()
        self.initUi()
        self.setupUi()
        self.initSchScene()
        self.openUser(skip=True)

    def initUser(self):
        self.user = UserAccount()

    def initUi(self):
        # Windows
        # self = main window = schematic editor window
        self.app.setWindowIcon(getIcon('eda'))
        self.centralWidget = None   # widget to put view on
        self.schView = None         # view to put scene on
        self.schScene = None        # scene to put symbols on
        self.cursorSymb = None      # symbol to insert

        # Menus
        self.menuBar = None
        self.menuFile = None
        self.menuEdit = None
        self.menuRun = None
        self.menuUser = None
        self.menuWave = None
        self.menuLayout = None
        self.menuHelp = None

        # Menu File
        self.actNewSch = None
        self.actSaveSch = None
        self.actLoadSch = None
        self.actSaveDesign = None
        self.actLoadDesign = None

        # Menu Edit
        self.actBasic = None
        self.actPdk = None
        self.actIp = None
        self.actDesign = None

        self.actRes = None
        self.actCap = None
        self.actDio = None
        self.actInd = None
        self.actGnd = None
        self.actVsrc = None
        self.actWire = None
        self.actWname = None
        self.actPin = None
        self.actRect = None
        self.actCmd = None
        self.actCmt = None
        self.actFit = None
        self.actZoomIn = None
        self.actZoomOut = None
        self.actGrid = None
        self.actMove = None

        # Menu Run
        self.actNetlist = None
        self.actRunSim = None
        self.actRunLay = None
        self.actStopSimLay = None

        # Menu User Account
        self.actLogin = None

        # Menu Wave
        self.actOpenWave = None

        # Menu Layout
        self.actOpenLayout = None

        # Menu Help
        self.actHelp = None

        # Status Bar
        self.statBar = None
        self.trademark = None


    def setupUi(self):
        self.resize(800, 600)
        self.setWindowTitle(f'{PRODUCT_NAME} - Schematic Editor')
        self.cursorSymb = 'NA'

        self.setupUiAction()
        self.setupUiMenu()
        self.setupStatBar()

    def setupUiAction(self):
        self.actSaveDesign = QAction(text='Save Design')
        self.actSaveDesign.triggered.connect(self.saveDesign)

        self.actLoadDesign = QAction(text='Load Design')
        self.actLoadDesign.triggered.connect(self.loadDesign)

        self.actNewSch = QAction(text='New Schematic')
        self.actNewSch.setShortcut(QKeySequence('ctrl+i'))
        self.actNewSch.triggered.connect(self.newSch)

        self.actSaveSch = QAction(text='Save Schematic')
        self.actSaveSch.setShortcut(QKeySequence('ctrl+s'))
        self.actSaveSch.triggered.connect(self.saveSch)

        self.actLoadSch = QAction(text='Load Schematic')
        self.actLoadSch.setShortcut(QKeySequence('ctrl+o'))
        self.actLoadSch.triggered.connect(self.loadSch)

        self.actBasic = QAction(text='Add Standard Component...')
        self.actBasic.setShortcut(QKeySequence('f2'))
        self.actBasic.triggered.connect(self.addBasicDev)

        self.actPdk = QAction(text='Add PDK Component...')
        self.actPdk.setShortcut(QKeySequence('f3'))
        self.actPdk.triggered.connect(self.addPdkDev)

        self.actIp = QAction(text='Add IP Component...')
        self.actIp.setShortcut(QKeySequence('f4'))
        self.actIp.triggered.connect(self.addIpDev)

        self.actDesign = QAction(text='Add Design Component...')
        self.actDesign.setShortcut(QKeySequence('f5'))
        self.actDesign.triggered.connect(self.addDesignDev)

        self.actRes = QAction(getIcon('res'), '&', self, 
                              text='Resistor')
        self.actRes.setShortcut(QKeySequence('r'))
        self.actRes.triggered.connect(self.drawRes)

        self.actCap = QAction(getIcon('cap'), '&', self, 
                              text='Capacitor')
        self.actCap.setShortcut(QKeySequence('c'))
        self.actCap.triggered.connect(self.drawCap)

        self.actDio = QAction(getIcon('dio'), '&', self, 
                              text='Diode')
        self.actDio.setShortcut(QKeySequence('d'))
        self.actDio.triggered.connect(self.drawDio)

        self.actInd = QAction(getIcon('ind'), '&', self, 
                              text='Inductor')
        self.actInd.setShortcut(QKeySequence('l'))
        self.actInd.triggered.connect(self.drawInd)

        self.actVsrc = QAction(getIcon('vsrc'), '&', self, 
                               text='Voltage Source')
        self.actVsrc.setShortcut(QKeySequence('v'))
        self.actVsrc.triggered.connect(self.drawVsrc)

        self.actGnd = QAction(getIcon('gnd'), '&', self,
                              text='Ground')
        self.actGnd.setShortcut(QKeySequence('g'))
        self.actGnd.triggered.connect(self.drawGnd)

        self.actWire = QAction(getIcon('wire'), '&', self,
                               text='Wire')
        self.actWire.setShortcut(QKeySequence('w'))
        self.actWire.triggered.connect(self.drawWire)

        self.actWname = QAction(getIcon('wname'), '&', self,
                               text='Wire Name')
        self.actWname.setShortcut(QKeySequence('ctrl+l'))
        self.actWname.triggered.connect(self.drawWname)

        self.actPin = QAction(getIcon('pin'), '&', self, 
                              text='Pin')
        self.actPin.setShortcut(QKeySequence('p'))
        self.actPin.triggered.connect(self.drawPin)

        self.actRect = QAction(getIcon('rect'), '&', self, 
                               text='Design Rectangle')
        self.actRect.setShortcut(QKeySequence('t'))
        self.actRect.triggered.connect(self.drawRect)

        self.actCmd = QAction(getIcon('cmd'), '&', self,
                              text='Simulation Command')
        self.actCmd.setShortcut(QKeySequence('s'))
        self.actCmd.triggered.connect(self.drawCmd)

        self.actCmt = QAction(getIcon('cmt'), '&', self,
                              text='Comment Text')
        self.actCmt.setShortcut(QKeySequence('m'))
        self.actCmt.triggered.connect(self.drawCmt)

        self.actFit = QAction(getIcon('fit'), '&', self,
                              text='Fit')
        self.actFit.setShortcut(QKeySequence('f'))
        self.actFit.triggered.connect(self.fit)

        self.actZoomIn = QAction(getIcon('zoom'), '&', self,
                               text='Zoom In')
        self.actZoomIn.setShortcut(QKeySequence('ctrl++'))
        self.actZoomIn.triggered.connect(self.zoomIn)

        self.actZoomOut = QAction(getIcon('zoom'), '&', self,
                               text='Zoom Out')
        self.actZoomOut.setShortcut(QKeySequence('ctrl+-'))
        self.actZoomOut.triggered.connect(self.zoomOut)

        self.actGrid = QAction(getIcon('grid'), '&', self,
                               text='Turn On/Off Grid')
        self.actGrid.setShortcut(QKeySequence('ctrl+g'))
        self.actGrid.triggered.connect(self.toggleGrid)

        self.actMove = QAction(text='Move')
        self.actMove.setShortcut(QKeySequence('f7'))
        self.actMove.triggered.connect(self.toggleMove)

        self.actRunSim = QAction(getIcon('run'), '&', self,
                                 text='Run Simulation')
        self.actRunSim.setShortcut(QKeySequence('ctrl+r'))
        self.actRunSim.triggered.connect(self.runSim)

        self.actRunLay = QAction(text='Run Auto Layout')
        self.actRunLay.setShortcut(QKeySequence('ctrl+y'))
        self.actRunLay.triggered.connect(self.runLay)

        self.actStopSimLay = QAction(text='Stop')
        self.actStopSimLay.setShortcut(QKeySequence('ctrl+h'))
        self.actStopSimLay.triggered.connect(self.stopSimLay)

        self.actNetlist = QAction(getIcon('netlist'), '&', self,
                                  text='View Netlist')
        self.actNetlist.setShortcut(QKeySequence('ctrl+n'))
        self.actNetlist.triggered.connect(self.showNetlist)

        self.actRotate = QAction(getIcon('rot'), '&', self,
                                 text='Rotate')
        self.actRotate.setShortcut(QKeySequence('ctrl+w'))
        self.actRotate.triggered.connect(self.rotateSymbol)

        self.actMirror = QAction(getIcon('mir'), '&', self,
                                 text='Mirror')
        self.actMirror.setShortcut(QKeySequence('ctrl+e'))
        self.actMirror.triggered.connect(self.mirrorSymbol)

        self.actLogin = QAction(text='Sign Up/In')
        self.actLogin.triggered.connect(self.openUser)

        self.actOpenWave = QAction(text='Open Wave')
        self.actOpenWave.triggered.connect(self.openWave)

        self.actOpenLayout = QAction(text='Open Layout')
        self.actOpenLayout.triggered.connect(self.openLayout)

        self.actHelp = QAction(text='Help')

    def setupUiMenu(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setTitle('File')
        self.menuFile.addAction(self.actNewSch)
        self.menuFile.addAction(self.actSaveSch)
        self.menuFile.addAction(self.actLoadSch)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actSaveDesign)
        self.menuFile.addAction(self.actLoadDesign)

        self.menuEdit = QMenu(self.menuBar)
        self.menuEdit.setTitle('Edit')

        self.menuEdit.addAction(self.actBasic)
        self.menuEdit.addAction(self.actPdk)
        self.menuEdit.addAction(self.actIp)
        self.menuEdit.addAction(self.actDesign)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actRes)
        self.menuEdit.addAction(self.actCap)
        self.menuEdit.addAction(self.actDio)
        self.menuEdit.addAction(self.actInd)
        self.menuEdit.addAction(self.actGnd)
        self.menuEdit.addAction(self.actVsrc)
        self.menuEdit.addAction(self.actWire)
        self.menuEdit.addAction(self.actWname)
        self.menuEdit.addAction(self.actPin)
        self.menuEdit.addAction(self.actRect)
        self.menuEdit.addAction(self.actCmd)
        self.menuEdit.addAction(self.actCmt)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actFit)
        self.menuEdit.addAction(self.actZoomIn)
        self.menuEdit.addAction(self.actZoomOut)
        self.menuEdit.addAction(self.actGrid)
        self.menuEdit.addAction(self.actRotate)
        self.menuEdit.addAction(self.actMirror)
        self.menuEdit.addAction(self.actMove)

        self.menuRun = QMenu(self.menuBar)
        self.menuRun.setTitle('Run')
        self.menuRun.addAction(self.actNetlist)
        self.menuRun.addSeparator()
        self.menuRun.addAction(self.actRunSim)
        self.menuRun.addAction(self.actRunLay)
        self.menuRun.addAction(self.actStopSimLay)

        self.menuUser = QMenu(self.menuBar)
        self.menuUser.setTitle('Guest (Lvl1)')
        self.menuUser.addAction(self.actLogin)
        self.menuWave = QMenu(self.menuBar)
        self.menuWave.setTitle('Wave')
        self.menuWave.addAction(self.actOpenWave)

        self.menuLayout = QMenu(self.menuBar)
        self.menuLayout.setTitle('Layout')
        self.menuLayout.addAction(self.actOpenLayout)

        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setTitle('Help')
        self.menuHelp.addAction(self.actHelp)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuRun.menuAction())
        self.menuBar.addAction(self.menuUser.menuAction())
        self.menuBar.addAction(self.menuWave.menuAction())
        self.menuBar.addAction(self.menuLayout.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())

        self.centralWidget = QWidget(self)
        self.centralView = QGraphicsView(self.centralWidget)
        self.centralView.setGeometry(QRect(0, 0, 500, 500))
        self.setCentralWidget(self.centralWidget)

    def setupStatBar(self):
        self.statBar = self.statusBar()
        self.trademark = QLabel()
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.trademark.sizePolicy().hasHeightForWidth())
        self.trademark.setPixmap(getTrademark())
        self.trademark.setMaximumSize(216, 40)
        self.trademark.setMinimumSize(216, 40)
        self.trademark.setScaledContents(True)
        self.statBar.addPermanentWidget(self.trademark)
        self.statBar.setStyleSheet('QStatusBar::item { border: none; }')
        setStatus(f'Welcome to {PRODUCT_NAME}', bar=self.statBar)

    def saveDesign(self, _):
        if self.schScene is None:
            return
        if self.schScene.editDesign is None:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Alert")
            msgBox.setText("There is no design in editing")
            msgBox.exec()
            return
        dialog = DesignFileDialog(self, 'Save Design as ...', mode='save', directory='./project/')
        result = dialog.exec()
        if result != dialog.accepted:
            return False
        designFile = dialog.selectedFiles()[0]
        self.schScene.editDesign.dumpDesign(designFile)
        self.schScene.editDesign.change_to_readonly()
        self.schScene.editDesign.info.setPosInDesign()
        self.schScene.editDesign.make_group()
        self.schScene.designs.append(self.schScene.editDesign)
        self.schScene.editDesign = None
        setStatus('Save Design to {}'.format(designFile))

    def loadDesign(self, _):
        self.schScene.cleanCursorSymb()
        dialog = DesignFileDialog(self, 'Load Design from ...', mode='load', directory='./project/')
        result = dialog.exec()
        if result != dialog.accepted:
            return False
        designFile = dialog.selectedFiles()[0]
        self.schScene.insertSymbType = 'Design'
        self.schScene.designTextLines = [line for line in readFile(designFile)]
        setStatus('Load Design from {}'.format(designFile))

    def newSch(self):
        if self.schScene is not None and len(self.schScene.items()) > 0:
            confirm = Confirmation('This will clean up current schematic, do you want to continue?')
            if confirm.exec():
                self.schScene = None
            else:
                return
        self.initSchScene()


    def saveSch(self):
        if self.schScene is None:
            return
        if self.schScene.editDesign is not None:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Alert")
            msgBox.setText("A design is in editing, please save it firstly")
            msgBox.exec()
            return

        if self.schScene.schFile is None:
            dialog = DesignFileDialog(self, 'Save Schematic as ...', mode='save', directory='./project/', type='sch')
            result = dialog.exec()
            if result != dialog.accepted:
                return False
            self.schScene.schFile = dialog.selectedFiles()[0]
        self.schScene.dumpSch(self.schScene.schFile)
        setStatus('Save Schematic to {}'.format(self.schScene.schFile))


    def loadSch(self):
        if len(self.schScene.items()) > 0:
            confirm = Confirmation('This will clean up current schematic, do you want to continue?')
            if confirm.exec():
                self.do_loadSch()
            else:
                pass
        else:
            self.do_loadSch()

    def do_loadSch(self):
        dialog = DesignFileDialog(self, 'Load Schematic from ...', mode='load', directory='./project/', type='sch')
        result = dialog.exec()
        if result != dialog.accepted:
            return False
        schFile = dialog.selectedFiles()[0]
        self.schScene = None
        self.initSchScene()
        self.schScene.makeSch([line for line in readFile(schFile)])
        self.schView.fit(self.schScene)
        self.schScene.schFile = schFile
        setStatus('Load Schematic from {}'.format(schFile))

    def drawDesign(self, model):
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbType = 'Design'
        self.schScene.designTextLines = self.schScene.designSymbols[model]

    def initSchScene(self):
        if self.schScene is None:
            self.schScene = SchScene(self)
            self.schView = SchView(self.schScene)
            self.setCentralWidget(self.schView)
            self.schScene.wavWin = WaveformViewer()
            self.schScene.layWin = LayoutMainWindow()

    def addBasicDev(self):
        self.schScene.cleanCursorSymb()
        devices = self.schScene.basicSymbolNames
        devInfo = self.schScene.basicDevInfo
        dialog = DeviceChoiceDialog(self, 'Add Standard Component', 
                                    devices=devices, 
                                    devInfo=devInfo,
                                    symbType='basic')
        result = dialog.exec()
        if result != dialog.accepted:
            return False
        self.drawSymbol(dialog.device, 'basic')
        setStatus('Select standard device {}'.format(dialog.device))
    
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
        setStatus('Select PDK device {}'.format(dialog.device))

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
        setStatus('Select IP device {}'.format(dialog.device))

    def addDesignDev(self):
        self.schScene.cleanCursorSymb()
        self.schScene.initDesignDevices()
        devices = sorted(self.schScene.designSymbols.keys())
        devInfo = None
        dialog = DeviceChoiceDialog(self, 'Add Design Component',
                                    devices=devices,
                                    devInfo=devInfo,
                                    symbType='design')
        result = dialog.exec()
        if result != dialog.accepted:
            return False
        self.drawDesign(dialog.device)
        setStatus('Select Design device {}'.format(dialog.device))

    def drawRes(self):
        self.drawSymbol('RES', 'basic')

    def drawCap(self):
        self.drawSymbol('CAP', 'basic')

    def drawDio(self):
        self.drawSymbol('DIO', 'basic')

    def drawInd(self):
        self.drawSymbol('IND1', 'basic')

    def drawVsrc(self):
        self.drawSymbol('VSRC', 'basic')

    def drawGnd(self):
        self.drawSymbol('GND', 'basic')

    def drawWire(self):
        self.drawSymbol('NA', 'W')

    def drawWname(self):
        self.schScene.drawWireName()
        
    def drawPin(self):
        self.drawSymbol('NA', 'P')
        
    def drawCmd(self):
        self.drawSymbol('NA', 'S')

    def drawCmt(self):
        self.drawSymbol('NA', 'M')

    def drawRect(self):
        self.schScene.cleanCursorSymb()
        if self.schScene.anyUnSavedDesign():
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Alert")
            msgBox.setText("There is unsaved design, can't draw another design")
            msgBox.exec()
        else:
            self.schScene.insertSymbType = 'RECT'

    def drawSymbol(self, name, symbType):
        self.schScene.cleanCursorSymb()
        self.schScene.insertSymbName = name
        self.schScene.insertSymbType = symbType

    def fit(self):
        self.schView.fit(self.schScene)
        setStatus('Auto-fit schematic to window size')

    def zoomIn(self):
        self.schView.zoom()
        setStatus('Zoom in')

    def zoomOut(self):
        self.schView.zoom(out=True)
        setStatus('Zoom out')

    def toggleGrid(self):
        self.schScene.toggleGrid()

    def toggleMove(self):
        self.schScene.toggleMove()

    def runSim(self):
        self.schScene.runSim()

    def runLay(self):
        self.schScene.runLay()

    def stopSimLay(self):
        self.schScene.cutGateway()

    def showNetlist(self):
        self.schScene.showNetlist()

    def rotateSymbol(self):
        item =  self.schScene.cursorSymb
        if item is None:
            self.schScene.rotateSelectedItems()
        elif isinstance(item, SchInst):
            item.setRotation(item.rotation()+90)

    def mirrorSymbol(self):
        item = self.schScene.cursorSymb
        if item is None:
            self.schScene.mirrorSelectedItems()

        elif isinstance(item, SchInst):
            t = item.transform()
            t.scale(-1,1)
            item.setTransform(t)

            p = item.paramText
            tp = p.transform()
            tp.scale(-1,1)
            tp.translate(-p.boundingRect().width(),0)
            p.setTransform(tp)

        elif isinstance(item, DesignBorder):
            if not item.design.readonly:
                return

            design = item.design
            t = item.transform()
            t.scale(-1,1)
            item.setTransform(t)
            for pin in design.Pins:
                pin.setTransform(t)
            for sym in design.symbols:
                sym.setTransform(t)
            for wire in design.wireList.wirelist:
                for seg in wire.getSegments():
                    seg.setTransform(t)
            for conn in design.connections:
                conn.setTransform(t)

        elif isinstance(item, DesignGroup):
            t = item.transform()
            t.scale(-1,1)
            item.setTransform(t)

    def openUser(self, skip=False):
        dialog = UserAccountDialog(self.user, skip=skip)
        result = dialog.exec()
        if result != dialog.accepted:
            return
        self.user.update(*dialog.info)
        if self.user.getLevel() == 2:
            self.menuUser.setTitle('{} (Lvl2)'.format(self.user.name))
            setStatus('Sign in as registered account: you can simulate with Standard & PDK components')
        elif self.user.getLevel() == 3:
            self.menuUser.setTitle('{} (Lvl3)'.format(self.user.name))
            setStatus('Sign in with authenticated account: you can simulate with all components')

    def openWave(self):
        dataFile = r"examples\wave\3855.sig"
        dataFile= r""
        self.schScene.wavWin.showWindowAndOpenWave(dataFile)
        setStatus('Open waveform viewer')

    def openLayout(self):
        dataFile = r"examples\layout\osc.gds"
        dataFile = r""
        self.schScene.layWin.show_window_and_open_gds(dataFile)
        setStatus("Open layout editor")