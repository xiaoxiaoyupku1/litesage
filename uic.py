

from typing import Optional
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, Signal,
    QSize, QTime, QUrl, Qt,QItemSelectionModel, QRectF, QDataStream, QFile,QIODevice)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient, QPen,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform, QStandardItemModel, QStandardItem, QPolygonF)
from PySide6.QtWidgets import (QApplication, QGraphicsView, QMainWindow, QMenu, QLabel, QGraphicsLineItem, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsEllipseItem,
    QMenuBar, QSizePolicy, QStatusBar, QWidget, QGridLayout, QListView, QListWidget, QGraphicsScene,QGraphicsView,QGraphicsTextItem,QGraphicsItem, 
    QFileDialog, QDialog, QInputDialog, QLineEdit)
from PySide6.QtCharts import QChart, QChartView, QLineSeries,QXYSeries,QValueAxis, QLogValueAxis
from PySide6.QtCore import QPointF

from wavefile import *
from tools import run_layout

import numpy as np
import pickle

scale=5
MIME_TYPES = ["text/plain"]

class Polygon(QGraphicsPolygonItem):
    def __init__(self, *args, **kwargs):
        QGraphicsPolygonItem.__init__(self, *args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

class Line(QGraphicsLineItem):
    def __init__(self, *args, **kwargs):
        QGraphicsLineItem.__init__(self, *args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

class Cycle(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        QGraphicsEllipseItem.__init__(self, *args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

class Rect(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        QGraphicsRectItem.__init__(self, *args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

class ScheScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.symbol = 'NA'
        self.doDel = False
        self.cursorSymbol=None
        self.widgetMouseMove = None
        self.symbols = []
        self.wireStartPos = None
        self.rectStartPos = None
        self.rect = None
        self.design = []

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.cleanCursorSymbol()
        elif event.key() == Qt.Key_Delete:
            self.delSymbol()

    def delSymbol(self):
        self.cleanCursorSymbol()

        for item in self.selectedItems():
            item_in_a_symbol = False
            for symbol in self.symbols:
                if item in symbol:
                    item_in_a_symbol = True
                    for i in symbol:
                        self.removeItem(i)
            if not item_in_a_symbol:
                self.removeItem(item)

    
    def mousePressEvent(self, event) -> None:
        if self.doDel:
            pass
        else:
            if self.symbol == 'R':
                self.wireStartPos = None
                self.painR(event)
                #print("85")
                #print(self.cursorSymbol[0])
            elif self.symbol == 'G':
                self.wireStartPos = None
                self.painG(event)
            elif self.symbol == 'V':
                self.wireStartPos = None
                self.painV(event)
            elif self.symbol == 'W':
                self.painW(event)
            elif self.symbol == 'P':
                self.painP(event)
            elif self.symbol == 'RECT':
                self.painRect(event)
            elif self.symbol == 'Design':
                self.painDesign(event)
            elif self.symbol == 'S':
                self.painS(event)

        return super().mousePressEvent(event)


    def mouseMoveEvent(self, event) -> None:
        if self.cursorSymbol is None:
            #print(self.cursorSymbol)
            if self.symbol == 'R':
                self.painR(event)
            elif self.symbol == 'G':
                self.painG(event)
            elif self.symbol == 'V':
                self.painV(event)
            elif self.symbol == 'P':
                self.painP(event)
            elif self.symbol == 'W':
                self.painW(event, mode='move')
            elif self.symbol == 'RECT':
                self.painRect(event, mode='move')
            elif self.symbol == 'Design':
                self.painDesign(event)
            elif self.symbol == 'S':
                self.painS(event)
        else:
            #print("115")
            #print(self.cursorSymbol[0])
            for item in self.cursorSymbol:
                item.setPos(event.scenePos())

        return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.symbol == 'W':
            self.wireStartPos = None

    def painDesign(self, event):
        self.cursorSymbol = []
        for item_def in self.design:
            item_def = item_def.rstrip()
            name, parameters = item_def.split(':')
            if name == 'Line':
                ps = [float(p) for p in parameters.split(',')]
                item = Line(*ps)
            elif name == 'Rect':
                ps = [float(p) for p in parameters.split(',')]
                item = Rect(*ps)
            elif name == 'Polygon':
                points = parameters.split(';')
                polygonf = QPolygonF()
                for point in points:
                    point_array = [float(i) for i in point.split(',')]
                    polygonf.append(QPointF(*point_array))
                item = Polygon(polygonf)
            elif name == 'Cycle':
                ps = [float(p) for p in parameters.split(',')]
                item = Cycle(*ps)
            elif name == 'RECT':
                ps = [float(p) for p in parameters.split(',')]
                item = Rect(*ps)
                pen = QPen()
                pen.setWidth(8)
                pen.setColor('green')
                item.setPen(pen)

            self.addItem(item)
            self.cursorSymbol.append(item)
            item.setPos(event.scenePos())

        self.symbols.append(self.cursorSymbol)

    def painR(self, event):
        self.cursorSymbol = []
        lines=[[0.000000,375.000000,0.000000,300.000000], 
               [0.000000,300.000000,-62.500000,281.250000], 
               [-62.500000,281.250000,62.500000,243.750000], 
               [62.500000,243.750000,-62.500000,206.250000],
               [-62.500000,206.250000,62.500000,168.750000], 
               [62.500000,168.750000,-62.500000,131.250000], 
               [-62.500000,131.250000,62.500000,93.750000], 
               [62.500000,93.750000,0.000000,75.000000], 
               [0.000000,75.000000,0.000000,0.000000]]
        for line in lines:
            line = [l/scale for l in line]
            line = Line(*line)
            self.addItem(line)
            self.cursorSymbol.append(line)
            line.setPos(event.scenePos())
        pin1=Rect(0-20/scale, 375/scale,40/scale,40/scale)
        self.addItem(pin1)
        self.cursorSymbol.append(pin1)
        pin1.setPos(event.scenePos())
        pin2=Rect(0-20/scale, 0-40/scale,40/scale,40/scale)
        self.addItem(pin2)
        self.cursorSymbol.append(pin2)
        pin2.setPos(event.scenePos())

        name = QGraphicsTextItem('    R1')
        self.addItem(name)
        self.cursorSymbol.append(name)
        #x = event.scenePos().x()
        #y = event.scenePos().y()
        name.setPos(event.scenePos())

        self.symbols.append(self.cursorSymbol)


    def painG(self, event):
        self.cursorSymbol = []
        points=[[-62.500000,187.500000], [62.500000,187.500000], [0.000000,250.000000]]
        polygonf = QPolygonF()
        for point in points:
            polygonf.append(QPointF(point[0]/scale,point[1]/scale))
        ground = Polygon(polygonf)
        self.addItem(ground)
        self.cursorSymbol.append(ground)
        ground.setPos(event.scenePos())

        line=[0.000000,0.000000,0.000000,187.500000]
        line = [l/scale for l in line]
        line = Line(*line)
        self.addItem(line)
        self.cursorSymbol.append(line)
        line.setPos(event.scenePos())

        pin=Rect(0-20/scale, 0-40/scale,40/scale,40/scale)
        self.addItem(pin)
        self.cursorSymbol.append(pin)
        pin.setPos(event.scenePos())
        self.symbols.append(self.cursorSymbol)

    def painV(self, event):
        self.cursorSymbol = []
        lines = [[0.000000,175.000000,0.000000,137.500000],
                 [18.750000,156.250000,-18.750000,156.250000],
                 [0.000000,125.000000,0.000000,0.000000],
                 [0.000000,250.000000,0.000000,375.000000],
                 [18.750000,218.750000,-18.750000,218.750000]]
        for line in lines:
            line = [l/scale for l in line]
            line = Line(*line)
            self.addItem(line)
            self.cursorSymbol.append(line)
            line.setPos(event.scenePos())
        cp=[p/scale for p in [0.000000,187.500000,68.750000]]
        cycle = Cycle(cp[0]-cp[2], cp[1]-cp[2], cp[2]*2,cp[2]*2)
        self.addItem(cycle)
        self.cursorSymbol.append(cycle)
        cycle.setPos(event.scenePos())

        pin1=Rect(0-20/scale, 375/scale,40/scale,40/scale)
        self.addItem(pin1)
        self.cursorSymbol.append(pin1)
        pin1.setPos(event.scenePos())
        pin2=Rect(0-20/scale, 0-40/scale,40/scale,40/scale)
        self.addItem(pin2)
        self.cursorSymbol.append(pin2)
        pin2.setPos(event.scenePos())

        name = QGraphicsTextItem('    V1')
        self.addItem(name)
        self.cursorSymbol.append(name)
        #x = event.scenePos().x()
        #y = event.scenePos().y()
        name.setPos(event.scenePos())

        self.symbols.append(self.cursorSymbol)

    def painP(self, event):
        self.cursorSymbol = []
        points = [[87.500000, 0.000000],
                  [31.250000, 56.250000],
                  [-31.250000, 56.250000],
                  [-87.500000, 0.000000],
                  [-31.250000, -56.250000],
                  [31.250000, -56.250000]]
        polygonf = QPolygonF()
        for point in points:
            polygonf.append(QPointF(point[0]/scale, point[1]/scale))
        iopin = Polygon(polygonf)
        iopin.setPen(QPen('red'))
        iopin.setBrush(QColor('red'))
        self.addItem(iopin)
        self.cursorSymbol.append(iopin)
        iopin.setPos(event.scenePos())

        self.symbols.append(self.cursorSymbol)

    def cleanCursorSymbol(self):
        if self.cursorSymbol is not None:
            for item in self.cursorSymbol:
                self.removeItem(item)
            self.cursorSymbol=None
        self.symbol = 'NA'
        self.wireStartPos = None
        self.rectStartPos = None

    def painW(self, event, mode=None):
        # mode: 'press', 'move'
        curPos = event.scenePos()
        curX, curY = curPos.x(), curPos.y()

        if self.widgetMouseMove is not None:
            self.removeItem(self.widgetMouseMove)

        if self.wireStartPos is None:
            if mode != 'move':
                self.wireStartPos = [curX, curY]
            return

        diffX = abs(curX - self.wireStartPos[0])
        diffY = abs(curY - self.wireStartPos[1])
        if diffX <= diffY:
            endPos = [self.wireStartPos[0], curY]
        else:
            endPos = [curX, self.wireStartPos[1]]
        line = self.wireStartPos + endPos
        line = Line(*line)
        line.setPen(QColor('blue'))
        self.addItem(line)

        if mode == 'move':
            self.widgetMouseMove = line
        else:
            self.wireStartPos = endPos

    def painRect(self, event, mode=None):
        # mode: 'press', 'move'
        curPos = event.scenePos()
        curX, curY = curPos.x(), curPos.y()

        if self.widgetMouseMove is not None:
            self.removeItem(self.widgetMouseMove)

        if self.rectStartPos is None: 
            if mode != 'move':
                self.rectStartPos = [curX, curY]
            return
        
        # leftTop is (0, 0)
        width = abs(curX - self.rectStartPos[0])
        height = abs(curY - self.rectStartPos[1])
        startX = min(curX, self.rectStartPos[0])
        startY = min(curY, self.rectStartPos[1])
        rect = QGraphicsRectItem(startX, startY, width, height)
        pen = QPen()
        pen.setWidth(8)
        pen.setColor('green')
        rect.setPen(pen)
        self.addItem(rect)

        if mode == 'move' :
            self.widgetMouseMove = rect
        else:
            self.rectStartPos = None
            self.rect = rect
    
    def painS(self, event):
        self.cursorSymbol = []
        text, ok = QInputDialog.getText(None, 
                                        'SPICE Analysis', 
                                        'Simulation command:',
                                        QLineEdit.Normal,
                                        '.dc temp -5 50 1')
        if not ok or len(text.strip()) == 0:
            return
        item = QGraphicsTextItem(text)
        item.setDefaultTextColor('darkblue')
        font = item.font()
        font.setPixelSize(50)
        item.setFont(font)
        item.setPos(event.scenePos())
        self.addItem(item)
        self.cursorSymbol.append(item)
        self.symbols.append(self.cursorSymbol)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(494, 354)
        
        self.MainWindow = MainWindow
        self.waveform_window = None

        self.symbol = "NA"
        self.label = None
        self.scene = None

        self.actionSave = QAction(QIcon("img/save.png"),"&",self)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave.triggered.connect(self.saveDesign)

        self.actionLoad = QAction(QIcon("img/load.png"),"&",self)
        self.actionLoad.setObjectName(u"actionLoad")
        self.actionLoad.triggered.connect(self.loadDesign)

        self.actionR = QAction(QIcon("img/r.png"), "&", self)
        self.actionR.setObjectName(u"actionR")
        self.actionR.setShortcut(QKeySequence('r'))
        self.actionR.triggered.connect(self.showR)

        self.actionG = QAction(QIcon("img/g.png"), "&", self)
        self.actionG.setObjectName(u"actionG")
        self.actionG.setShortcut(QKeySequence('g'))
        self.actionG.triggered.connect(self.showG)

        self.actionV = QAction(QIcon("img/v.png"), "&", self)
        self.actionV.setObjectName(u"actionV")
        self.actionV.setShortcut(QKeySequence('v'))
        self.actionV.triggered.connect(self.showV)

        self.actionW = QAction(QIcon("img/w.png"), "&", self)
        self.actionW.setObjectName(u"actionW")
        self.actionW.setShortcut(QKeySequence('w'))
        self.actionW.triggered.connect(self.showW)

        self.actionP = QAction(QIcon("img/p.png"), "&", self)
        self.actionP.setObjectName(u"actionP")
        self.actionP.setShortcut(QKeySequence('p'))
        self.actionP.triggered.connect(self.showP)

        self.actionRect = QAction(QIcon("img/rect.png"), "&", self)
        self.actionRect.setObjectName(u"actionRect")
        self.actionRect.setShortcut(QKeySequence('t'))
        self.actionRect.triggered.connect(self.showRect)

        self.actionS = QAction(QIcon("img/s.png"), "&", self)
        self.actionS.setObjectName(u"actionS")
        self.actionS.setShortcut(QKeySequence('s'))
        self.actionS.triggered.connect(self.showS)

        """
        self.actionDEL = QAction(QIcon("img/del.png"), "&", self)
        self.actionDEL.setObjectName(u"actionDEL")
        self.actionDEL.setShortcut(QKeySequence('Del'))
        self.actionDEL.triggered.connect(self.delSymbol)
        """

        self.actionShowWave = QAction(text='Show')
        self.actionShowWave.triggered.connect(self.showwave)

        self.actionShowLayout = QAction(text='Open')
        self.actionShowLayout.triggered.connect(self.showlayout)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        self.graphicsView = QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setGeometry(QRect(0, 0, 491, 331))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 494, 18))

        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menuBar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuWave = QMenu(self.menuBar)
        self.menuWave.setObjectName(u"menuWave")
        self.menuLayout = QMenu(self.menuBar)
        self.menuLayout.setObjectName(u"menuLayout")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuWave.menuAction())
        self.menuBar.addAction(self.menuLayout.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionLoad)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionR)
        self.menuEdit.addAction(self.actionG)
        self.menuEdit.addAction(self.actionV)
        self.menuEdit.addAction(self.actionW)
        self.menuEdit.addAction(self.actionP)
        self.menuEdit.addAction(self.actionRect)
        self.menuEdit.addAction(self.actionS)
        #self.menuEdit.addAction(self.actionDEL)

        self.menuWave.addAction(self.actionShowWave)
        self.menuLayout.addAction(self.actionShowLayout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        title = 'FOOHU EDA - Schematic Editor'
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", title, None))
        self.actionR.setText(QCoreApplication.translate("MainWindow", u"Resistor", None))
        self.actionG.setText(QCoreApplication.translate("MainWindow", u"Ground", None))
        self.actionV.setText(QCoreApplication.translate("MainWindow", u"VoltageSource", None))
        self.actionW.setText(QCoreApplication.translate("MainWindow", u"Wire", None))
        self.actionP.setText(QCoreApplication.translate("MainWindow", u"Pin", None))
        self.actionRect.setText(QCoreApplication.translate("MainWindow", u"Rectangle", None))
        self.actionS.setText(QCoreApplication.translate("MainWindow", u"SimCommand", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save Design", None))
        self.actionLoad.setText(QCoreApplication.translate("MainWindow", u"Load Design", None))
        #self.actionDEL.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuWave.setTitle(QCoreApplication.translate("MainWindow", u"Wave", None))
        self.menuLayout.setTitle(QCoreApplication.translate("MainWindow", u"Layout", None))

    def createScene(self):
        self.scene = ScheScene()
        self.scene.setSceneRect(QRectF(0, 0, 500, 500))
        self.view = QGraphicsView(self.scene)
        self.view.setMouseTracking(True)
        self.MainWindow.setCentralWidget(self.view)


    def saveDesign(self, s):
        if self.scene is not None and self.scene.rect is not None:
            file_dialog = QFileDialog(self, "Save as...")
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setMimeTypeFilters(MIME_TYPES)
            if file_dialog.exec() != QDialog.Accepted:
                return False
            fn = file_dialog.selectedFiles()[0]

            items = self.scene.rect.collidingItems()
            rect = self.scene.rect.rect()
            center_x = rect.x() + rect.width()/2
            center_y = rect.y() + rect.height()/2
            with open(fn,'w') as OUT:
                OUT.write("RECT:")
                OUT.write(','.join([str(i) for i in [rect.x()-center_x,rect.y()-center_y,rect.width(),rect.height()]]))
                OUT.write('\n')
                for item in items:
                    out_str = ''
                    if type(item) is Line:
                        item_x = item.pos().x()
                        item_y = item.pos().y()
                        line = item.line()
                        out_str = "Line:"
                        out_str += ','.join([str(p) for p in [line.x1() + item_x - center_x, 
                                                              line.y1() + item_y - center_y, 
                                                              line.x2() + item_x - center_x, 
                                                              line.y2() + item_y - center_y]])
                        OUT.write(out_str)
                        OUT.write('\n')
                    elif type(item) is Rect:
                        item_x = item.pos().x()
                        item_y = item.pos().y()
                        out_str  = "Rect:" +  str(item.rect().x() + item_x - center_x) 
                        out_str += ',' 
                        out_str += str(item.rect().y() + item_y - center_y) 
                        out_str += ',' 
                        out_str += str(item.rect().width())
                        out_str += ',' 
                        out_str += str(item.rect().height())
                        OUT.write(out_str)
                        OUT.write('\n')
                    elif type(item) is Polygon:
                        item_x = item.pos().x()
                        item_y = item.pos().y()
                        out_str = "Polygon:"
                        outs=[]
                        for point in item.polygon().toList():
                            point_str = str(point.x() + item_x - center_x) + ',' + str(point.y() + item_y - center_y)
                            outs.append(point_str)
                        out_str += ';'.join(outs)
                        OUT.write(out_str)
                        OUT.write('\n')
                    elif type(item) is Cycle:
                        rect = item.rect()
                        out_str = "Cycle:"
                        outs = [str(rect.x() + item.x() - center_x), str(rect.y()+item.y()-center_y), str(rect.width()),str(rect.height())]
                        out_str += ','.join(outs)
                        OUT.write(out_str)
                        OUT.write('\n')

    def loadDesign(self, s):
        if self.scene is None:
            self.createScene()

        self.scene.cleanCursorSymbol()


        file_dialog = QFileDialog(self, "Load from...")
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setMimeTypeFilters(MIME_TYPES)
        if file_dialog.exec() != QDialog.Accepted:
            return False
        fn = file_dialog.selectedFiles()[0]

        self.scene.symbol = 'Design'

        with open(fn, 'r') as IN:
            self.scene.design = IN.readlines()

    def showR(self,s):
        if self.scene is None:
            self.createScene()

        self.scene.cleanCursorSymbol()
        self.scene.symbol = 'R'



    def showG(self,s):
        if self.scene is None:
            self.createScene()

        self.scene.cleanCursorSymbol()
        self.scene.symbol = 'G'

    def showV(self,s):
        if self.scene is None:
            self.createScene()
        self.scene.cleanCursorSymbol()
        self.scene.symbol = 'V'

    def showW(self, position):
        if self.scene is None:
            self.createScene()
        self.scene.cleanCursorSymbol()
        self.scene.symbol = 'W'

    def showP(self, s):
        if self.scene is None:
            self.createScene()
        self.scene.cleanCursorSymbol()
        self.scene.symbol = 'P'
    
    def showRect(self, position):
        if self.scene is None:
            self.createScene()
        self.scene.cleanCursorSymbol()
        self.scene.symbol = "RECT"

    def showS(self, position):
        if self.scene is None:
            self.createScene()
        self.scene.cleanCursorSymbol()
        self.scene.symbol = 'S'

    def showwave(self, s):
        #wavefile parse
        wavefile = '.\\examples\\wave\\waveform.tr0'
        handler = get_wavefile_handler(wavefile)
        handler.parseWavefile()

        self.signames=handler.get_signames()
        self.values=handler.getSigVals('tr')

        self.waveWidet = QWidget()

        #listview
        self.list_view = QListWidget()
        self.list_view.addItems(self.signames[1:])
        self.list_view.currentItemChanged.connect(self.doshowwave)

        #chartview
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.setTitle("Wave")

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.main_layout = QGridLayout(self.waveWidet)
        self.main_layout.addWidget(self.list_view, 1, 0)
        self.main_layout.addWidget(self.chart_view, 1, 1)
        self.main_layout.setColumnStretch(1, 1)
        self.main_layout.setColumnStretch(0, 0)

        if self.waveform_window is not None:
            self.waveform_window.destroy()
        self.waveform_window = WaveformWindow()
        self.waveform_window.update(self.main_layout)
        self.waveform_window.show()

    def doshowwave(self,index):
        signame = index.text()
        value_index = self.signames.index(signame)
        series = QLineSeries()
        series.appendNp(np.array(self.values[0]), np.array(self.values[value_index]))

        self.chart.removeAllSeries()
        self.chart.addSeries(series)
        self.chart.setTitle(signame)
        self.chart.createDefaultAxes()

    def showlayout(self):
        run_layout('.\\examples\\layout\\reference.gds')


class WaveformWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = None
        self.label = QLabel("Waveform Viewer")
        self.setWindowTitle('FOOHU EDA - Waveform Viewer')
        self.resize(900, 500)

    def update(self, layout):
        self.layout = layout
        self.setLayout(layout)
