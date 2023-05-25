

from typing import Optional
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt,QItemSelectionModel, QRectF)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QPen,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform, QStandardItemModel, QStandardItem)
from PySide6.QtWidgets import (QApplication, QGraphicsView, QMainWindow, QMenu, QLabel, QGraphicsLineItem,
    QGraphicsRectItem, QMenuBar, QSizePolicy, QStatusBar, QWidget, QGridLayout, QListView, QListWidget, QGraphicsScene,QGraphicsView)
from PySide6.QtCharts import QChart, QChartView, QLineSeries,QXYSeries,QValueAxis, QLogValueAxis
from PySide6.QtCore import QPointF

from wavefile import *
from tools import run_layout

import numpy as np

class ScheScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.symbol = 'NA'
        self.wireStartPos = None
        self.rectStartPos = None

    def mousePressEvent(self, event) -> None:
        pos = event.scenePos()
        if self.symbol == 'RR':
            self.wireStartPos = None
            self.painRR(event)
        elif self.symbol == 'WW':
            self.painWW(event)
        elif self.symbol == 'RECT':
            self.painRect(event)

    def mouseReleaseEvent(self, event):
        if self.symbol == 'RECT':
            self.painRect(event)

    def painRR(self, event):
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
            line = [l/10 for l in line]
            line = QGraphicsLineItem(*line)
            self.addItem(line)
            line.setPos(event.scenePos())

    def painWW(self, event):
        click = event.scenePos()
        clickX, clickY = click.x(), click.y()
        if self.wireStartPos is None:
            self.wireStartPos = [clickX, clickY]
        else:
            diffX = abs(clickX - self.wireStartPos[0])
            diffY = abs(clickY - self.wireStartPos[1])
            if diffX <= diffY:
                endPos = [self.wireStartPos[0], clickY]
            else:
                endPos = [clickX, self.wireStartPos[1]]
            line = self.wireStartPos + endPos
            line = QGraphicsLineItem(*line)
            line.setPen(QColor('blue'))
            self.addItem(line)
            self.wireStartPos = endPos

    def painRect(self, event):
        click = event.scenePos()
        clickX, clickY = click.x(), click.y()

        if self.rectStartPos is None:
            self.rectStartPos = [clickX, clickY]
            return

        width = abs(clickX - self.rectStartPos[0])
        height = abs(clickY - self.rectStartPos[1])
        startX = min(clickX, self.rectStartPos[0])
        startY = min(clickY, self.rectStartPos[1])
        # leftTop is (0, 0)
        rect = QGraphicsRectItem(startX, startY, width, height)
        pen = QPen()
        pen.setWidth(8)
        pen.setColor('red')
        rect.setPen(pen)
        self.addItem(rect)
        self.rectStartPos = None


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

        self.actionR = QAction(QIcon("r.png"), "&", self)
        self.actionR.setObjectName(u"actionR")
        self.actionR.setShortcut(QKeySequence('r'))
        self.actionR.triggered.connect(self.showR)

        self.actionG = QAction(QIcon("g.png"), "&", self)
        self.actionG.setObjectName(u"actionG")
        self.actionG.setShortcut(QKeySequence('g'))
        self.actionG.triggered.connect(self.showSchematic)

        self.actionW = QAction(QIcon("w.png"), "&", self)
        self.actionW.setObjectName(u"actionW")
        self.actionW.setShortcut(QKeySequence('w'))
        self.actionW.triggered.connect(self.showW)

        self.actionRect = QAction(QIcon("rect.png"), "&", self)
        self.actionRect.setObjectName(u"actionRect")
        self.actionRect.setShortcut(QKeySequence('t'))
        self.actionRect.triggered.connect(self.showRect)

        self.actionShowWave = QAction(text='Show')
        self.actionShowWave.triggered.connect(self.showwave)
        # self.actionShowWave.setCheckable(True)

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
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionR)
        self.menuEdit.addAction(self.actionG)
        self.menuEdit.addAction(self.actionW)
        self.menuEdit.addAction(self.actionRect)

        self.menuWave.addAction(self.actionShowWave)
        self.menuLayout.addAction(self.actionShowLayout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        title = 'FOOHU EDA - Schematic Editor'
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", title, None))
        self.actionR.setText(QCoreApplication.translate("MainWindow", u"Resistor", None))
        self.actionG.setText(QCoreApplication.translate("MainWindow", u"Ground", None))
        self.actionW.setText(QCoreApplication.translate("MainWindow", u"Wire", None))
        self.actionRect.setText(QCoreApplication.translate("MainWindow", u"Rectangle", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuWave.setTitle(QCoreApplication.translate("MainWindow", u"Wave", None))
        self.menuLayout.setTitle(QCoreApplication.translate("MainWindow", u"Layout", None))

    def showSchematic(self, s):
        if self.scene is None:
            self.scene = ScheScene()
            self.scene.setSceneRect(QRectF(0, 0, 500, 500))
            self.view = QGraphicsView(self.scene)
            self.MainWindow.setCentralWidget(self.view)
        self.scene.symbol = 'RR'

    def showR(self,s):
        if self.label is None:
            self.label = QLabel()
            self.canvas = QPixmap(490, 330)
            self.canvas.fill(Qt.white)
            self.label.setPixmap(self.canvas)
            self.MainWindow.setCentralWidget(self.label)
        self.symbol = "R"

    def showW(self, position):
        if self.scene is None:
            self.scene = ScheScene()
            self.scene.setSceneRect(QRectF(0, 0, 500, 500))
            self.view = QGraphicsView(self.scene)
            self.MainWindow.setCentralWidget(self.view)
        self.scene.symbol = 'WW'

    def showRect(self, position):
        self.showSchematic(position)
        self.scene.symbol = 'RECT'

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