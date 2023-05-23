

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt,QItemSelectionModel, QRectF)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform, QStandardItemModel, QStandardItem)
from PySide6.QtWidgets import (QApplication, QGraphicsView, QMainWindow, QMenu, QLabel, QGraphicsLineItem,
    QMenuBar, QSizePolicy, QStatusBar, QWidget, QGridLayout, QListView, QListWidget, QGraphicsScene,QGraphicsView)

from PySide6.QtCharts import QChart, QChartView, QLineSeries,QXYSeries,QValueAxis, QLogValueAxis


from PySide6.QtCore import QPointF

from wavefile import *

import numpy as np

class ScheScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.symbol = 'NA'

    def mousePressEvent(self, event) -> None:
        if self.symbol == 'RR':
            self.painRR(event)

    def painRR(self,event):
        lines=[[0.000000,375.000000,0.000000,300.000000], [0.000000,300.000000,-62.500000,281.250000], [-62.500000,281.250000,62.500000,243.750000], [62.500000,243.750000,-62.500000,206.250000], [-62.500000,206.250000,62.500000,168.750000], [62.500000,168.750000,-62.500000,131.250000], [-62.500000,131.250000,62.500000,93.750000], [62.500000,93.750000,0.000000,75.000000], [0.000000,75.000000,0.000000,0.000000]]
        for line in lines:
            line = [l/10 for l in line]
            line = QGraphicsLineItem(*line)
            self.addItem(line)
            line.setPos(event.scenePos())




class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(494, 354)
        
        self.MainWindow = MainWindow

        self.symbol = "NA"
        self.label = None
        self.scene = None

        self.actionR = QAction(QIcon("r.png"), "&", self)
        self.actionR.setObjectName(u"actionR")
        self.actionR.triggered.connect(self.showR)
        self.actionG = QAction(QIcon("g.png"), "&", self)
        self.actionG.setObjectName(u"actionG")
        self.actionG.triggered.connect(self.showSchematic)

        self.actionShowWave = QAction(text='show')
        self.actionShowWave.triggered.connect(self.showwave)
        self.actionShowWave.setCheckable(True)

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
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuWave.menuAction())
        self.menuFile.addSeparator()
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionR)
        self.menuEdit.addAction(self.actionG)

        self.menuWave.addAction(self.actionShowWave)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionR.setText(QCoreApplication.translate("MainWindow", u"R", None))
        self.actionG.setText(QCoreApplication.translate("MainWindow", u"G", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuWave.setTitle(QCoreApplication.translate("MainWindow", u"Wave", None))

    def showSchematic(self,s):
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

    def painR(self,position):
        lines=[[0.000000,375.000000,0.000000,300.000000], [0.000000,300.000000,-62.500000,281.250000], [-62.500000,281.250000,62.500000,243.750000], [62.500000,243.750000,-62.500000,206.250000], [-62.500000,206.250000,62.500000,168.750000], [62.500000,168.750000,-62.500000,131.250000], [-62.500000,131.250000,62.500000,93.750000], [62.500000,93.750000,0.000000,75.000000], [0.000000,75.000000,0.000000,0.000000]]


        painter = QPainter(self.canvas)
        for line in lines:
            line = [ l /10  for l in line]
            line = [line[0]+position.x(),line[1]+position.y(),line[2]+position.x(),line[3]+position.y()]
            painter.drawLine(*line)

        painter.end()
        self.label.setPixmap(self.canvas)
     


    
    def showwave(self, s):

        #wavefile parse
        wavefile = 'waveform.tr0'
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

        self.MainWindow.setCentralWidget(self.waveWidet)

    def doshowwave(self,index):
        print(index.text())
        value_index = self.signames.index(index.text())
        series = QLineSeries()
        series.appendNp(np.array(self.values[0]), np.array(self.values[value_index]))

        self.chart.removeAllSeries()
        self.chart.addSeries(series)

        self.chart.createDefaultAxes()
