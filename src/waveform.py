import os
from copy import deepcopy
from numpy import array as NDArray
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QMenuBar, QMenu, QListWidget, QGridLayout, QGraphicsScene, 
    QGraphicsView, QGraphicsItem, QGraphicsTextItem, 
    QFileDialog, QSizePolicy, QStatusBar, QLabel
)
from PySide6.QtCharts import (QChart, QLineSeries, QValueAxis, QLogValueAxis)
from PySide6.QtCore import Qt, QPointF, QRectF, QRect
from PySide6.QtGui import (
    QPainter, QFont, QFontMetrics, QPainterPath, QColor, QAction
)
from pickle import load, dump
from collections import defaultdict
import numpy as np
import math
from src.calculator import Calculator
from src.tool.wave import WaveInfo
from src.tool.config import PRODUCT_NAME
from src.tool.status import setStatus
from src.hmi.image import getTrademark
from src.hmi.dialog import WaveFileDialog


class WaveformViewer(QMainWindow):
    def __init__(self, mode='full'):
        super().__init__()
        self.menuBar = None
        self.menuFile = None
        self.menuView = None
        self.actLoad = None
        self.actSaveAs = None

        self.waveInfo = None
        self.simType = None
        self.sigNames = None
        self.sigValues = None
        self.listView: QListWidget = None
        self.chartView = None # wave signal chart
        self.statusBar = None
        self.centralWidget = None  # window layout of widgets
        self.gridLayout = None

        self.name2names = defaultdict(set)
        self.parseData(None, mode)
        self.setupUi()

        # TODO: make self an embedded window instead of an independent window
        #       embedded to its parent which is schWin (FoohuEda)
        self.setWindowTitle(f'{PRODUCT_NAME} - Waveform Viewer')
        self.resize(1000, 600)


    def showWindowAndOpenWave(self, dataFile, mode='full'):
        # dataFile: WaveInfo, path string, empty string, None

        # full: signames and sigvalues
        # names: only signames

        data = None
        if isinstance(dataFile, WaveInfo):
            data = dataFile
        else:
            if dataFile is None or not os.path.isfile(dataFile):
                dataFile = QFileDialog.getOpenFileName(self, caption='Open Wave File',
                                                       filter='Wave files (*.raw *.sig)')[0]
            if dataFile.endswith('.sig'):
                with open(dataFile, 'rb') as fport:
                    data = load(fport) # waveinfo
            elif dataFile.endswith('.raw'):
                data = WaveInfo(dataFile)
            elif len(dataFile) == 0:
                return
            else:
                assert 0, 'wrong dataFile format: {}'.format(dataFile)
            setStatus('Load Wave {}'.format(dataFile))

        self.parseData(data, mode)
        self.setupUi()
        self.show()

    def displayWave(self, sigName, sigType):
        for index, sig in enumerate(self.sigNames):
            if sig.lower().startswith(sigType) and sigName.lower() in sig.lower():
                item = self.listView.item(index-1)
                self.listView.setCurrentItem(item)
                self.changeWave()
                break
            
    def parseData(self, data, mode):
        if data is None:
            self.simType = 'dc'
            self.sigNames = []
            self.sigValues = NDArray(0)
            return
        elif mode == 'full':
            self.waveInfo = data
            self.simType = self.waveInfo.get_sim_type()
            self.sigNames= self.waveInfo.get_trace_names()
            self.sigValues = self.waveInfo.get_waves()
        elif mode == 'names':
            self.sigNames = data
            self.sigValues = NDArray((len(self.sigNames)))
            raise

    def updSignal(self, data):
        # self.sigValues
        # TODO
        raise

    def setupUi(self):
        self.menuBar = QMenuBar(self)
        self.actLoad = QAction(text='Load Wave')
        self.actLoad.setShortcut('ctrl+o')
        self.actLoad.triggered.connect(self.loadWave)
        self.actSaveAs = QAction(text='Save Wave as')
        self.actSaveAs.setShortcut('ctrl+shift+s')
        self.actSaveAs.triggered.connect(self.saveWave)
        self.setMenuBar(self.menuBar)
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setTitle('File')
        self.menuFile.addAction(self.actLoad)
        self.menuFile.addAction(self.actSaveAs)
        self.menuBar.addAction(self.menuFile.menuAction())

        self.actZoomIn = QAction(text='Zoom In')
        self.actZoomIn.setShortcut('ctrl++')
        self.actZoomIn.triggered.connect(self.zoom)
        self.actZoomOut = QAction(text='Zoom Out')
        self.actZoomOut.setShortcut('ctrl+-')
        self.actZoomOut.triggered.connect(self.zoomOut)
        self.menuView = QMenu(self.menuBar)
        self.menuView.setTitle('View')
        self.menuView.addAction(self.actZoomIn)
        self.menuView.addAction(self.actZoomOut)
        self.menuBar.addAction(self.menuView.menuAction())

        # Left side: wave name list
        if self.listView is None:
            self.listView = WaveListWidget(self)
        else:
            self.listView.clear()
        self.listView.addItems(self.sigNames[1:])
        self.listView.currentItemChanged.connect(self.changeWave)

        # Right side: wave signal chart
        if self.chartView is not None:
            self.chartView.destroy()
        self.chartView = ChartView(self)

        self.statusBar = QStatusBar()
        trademark = QLabel()
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(trademark.sizePolicy().hasHeightForWidth())
        trademark.setPixmap(getTrademark())
        trademark.setMaximumSize(216, 40)
        trademark.setMinimumSize(216, 40)
        trademark.setScaledContents(True)
        self.statusBar.addPermanentWidget(trademark)
        self.statusBar.setStyleSheet('QStatusBar::item { border: none; }')

        # Layout
        self.centralWidget = QWidget()
        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.addWidget(self.listView, 1, 0)
        self.gridLayout.setColumnStretch(0, 0)
        self.gridLayout.addWidget(self.chartView, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.addWidget(self.statusBar, 2, 0, 1, 2)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.centralWidget)

        # Select first signal
        self.listView.setCurrentRow(0)

    def changeWave(self):
        cur = self.listView.currentItem()
        if cur is None:
            return
        self.chartView.draw(cur.text(), *self.name2names[cur.text()])
        self.chartView.chart.setTitle(cur.text())

    def closeEvent(self, event):
        return super().closeEvent(event)

    def loadWave(self):
        dialog = WaveFileDialog(self, 'Load Wave', mode='load', directory='./project/')
        result = dialog.exec()
        if result != dialog.accepted:
            return
        waveFile = dialog.selectedFiles()[0]
        if not os.access(waveFile, os.R_OK):
            setStatus('No permission to read {}'.format(waveFile))
            return
        self.showWindowAndOpenWave(waveFile)
        setStatus('Load wave from {}'.format(waveFile))

    def saveWave(self):
        if len(self.sigNames) == 0 or self.waveInfo is None:
            setStatus('No wave to save!')
            return
        dialog = WaveFileDialog(self, 'Save Wave as', mode='save', directory='./project/')
        result = dialog.exec()
        if result != dialog.accepted:
            return
        waveFile = dialog.selectedFiles()[0]
        if not os.access(os.path.dirname(waveFile), os.W_OK):
            setStatus('No permission to write {}'.format(waveFile))
            return
        with open(waveFile, 'wb') as fport:
            dump(self.waveInfo, fport)
        setStatus('Save wave to {}'.format(waveFile))

    def zoom(self, out=False):
        if self.chartView is None:
            return
        factor = 0.8 if out else 1.2
        self.chartView.scale(factor, factor)

    def zoomOut(self):
        self.zoom(out=True)

class ChartView(QGraphicsView):
    def __init__(self, wavWin):
        super().__init__()
        self.wavWin = wavWin

        self.setScene(QGraphicsScene(self))

        self.chart = QChart()
        self.chart.setMinimumSize(640, 480)
        self.chart.legend().hide()
        self.chart.setAcceptHoverEvents(True)
        self.axisX = QValueAxis()
        self.axisX.setLabelFormat('%.3g')
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.axisY = QValueAxis()
        self.axisY.setLabelFormat('%.3g')
        self.chart.addAxis(self.axisY, Qt.AlignLeft)
        self.scene().addItem(self.chart)
        self.axisMinX = None
        self.axisMaxX = None
        self.axisMinY = None
        self.axisMaxY = None
        self.axisXLog = False
        self.axisYLog = False

        self.delta = WaveTextItem(self.chart)
        x, y = self.scene().sceneRect().bottomRight().toTuple()
        self.delta.setPos(x - 100, y - 100)
        self.delta.setZValue(15)
        
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)

        self.tooltip = Callout(self.chart)
        self.callouts = []

    def draw(self, *sigNames):
        self.chart.removeAllSeries()
        self.chart.removeAxis(self.axisX)
        self.chart.removeAxis(self.axisY)

        self.checkLogScale(sigNames)

        self.axisX = QLogValueAxis() if self.axisXLog else QValueAxis()
        self.axisX.setLabelFormat('%.2g')
        self.axisX.setLabelsVisible(True)
        self.chart.addAxis(self.axisX, Qt.AlignBottom)

        # self.axisY = QLogValueAxis() if self.axisYLog else QValueAxis()
        self.axisY = QValueAxis()
        self.axisY.setLabelFormat('%.2g')
        self.axisY.setLabelsVisible(True)
        self.chart.addAxis(self.axisY, Qt.AlignLeft)

        self.axisMinY = None
        self.axisMaxY = None

        xData = deepcopy(self.wavWin.sigValues[0])
        self.axisMaxX = max(xData)
        if self.axisMaxX <= 1 and self.axisMaxX > 1e-3:
            xData *= 1e3
            self.axisX.setLabelFormat('%.3gm')
        elif self.axisMaxX <= 1e-3 and self.axisMaxX > 1e-6:
            xData *= 1e6
            self.axisX.setLabelFormat('%.3gu')
        elif self.axisMaxX <= 1e-6:
            xData *= 1e9
            self.axisX.setLabelFormat('%.3gn')

        for sigName in sigNames:
            index = self.wavWin.sigNames.index(sigName)
            series = QLineSeries()
            series.setName(sigName)

            yData = self.wavWin.sigValues[index]
            yData = np.where(np.abs(yData) < 1e-14, 0, yData)
            self.axisMinY = min(yData) if self.axisMinY is None else min(self.axisMinY, min(yData))
            self.axisMaxY = max(yData) if self.axisMaxY is None else max(self.axisMaxY, max(yData))

            series.appendNp(xData, yData)
            self.chart.addSeries(series)
            series.attachAxis(self.axisX)
            series.attachAxis(self.axisY)
            series.clicked.connect(self.wave_point_selected)
            series.hovered.connect(lambda p, s, name=series.name(): self.wave_hovered(p, s, name))

        if len(sigNames) > 1:
            self.chart.legend().show()
        else:
            self.chart.legend().hide()
        self.setAxesRange()

        for callout in self.callouts:
            self.scene().removeItem(callout)
        self.callouts = []
        self.tooltip.hide()
        self.delta.setHtml("")
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setAxesTitles()

    def checkLogScale(self, sigNames):
        self.axisXLog = True if self.wavWin.simType.startswith('ac') else False
        self.axisYLog = any(sigName.lower().startswith(('is(', 'ib(')) for sigName in sigNames) 

    def setAxesRange(self):
        self.axisX.setTickCount(5)
        self.axisY.setTickCount(5)

        if math.isclose(self.axisMaxY, self.axisMinY):
            if math.isclose(self.axisMaxY, 0.):
                self.axisY.setRange(-1., 1.)
                return
            else:
                half = abs(self.axisMaxY)
                self.axisMaxY, self.axisMinY = self.axisMaxY + half, self.axisMinY - half
        
        if self.axisMaxY == 0:
            maxy = 0
        else:
            maxy = f'{self.axisMaxY:.3e}'
            maxy_int, maxy_flo = maxy.split('e')
            maxy_int = str(int(float(maxy_int)) + 1)
            maxy = eval(maxy_int + 'e' + maxy_flo)

        if self.axisMinY == 0:
            miny = 0
        else:
            miny = f'{self.axisMinY:.3e}'
            miny_int, miny_flo = miny.split('e')
            miny_int = str(int(float(miny_int)) - 1)
            miny = eval(miny_int + 'e' + miny_flo)

        if maxy - miny < 1.5e-12:
            # need update, not good
            # to fix no y-axis if max-min too small
            maxy = miny + 1.5e-12

        self.axisY.setRange(miny, maxy)

    def showCalculator(self):
        x0, y0 = self.callouts[0].x, self.callouts[0].y
        x1, y1 = self.callouts[1].x, self.callouts[1].y
        self.calculator = Calculator(x0,y0,x1,y1)
        self.calculator.show()

    def resizeEvent(self, event):
        self.scene().setSceneRect(QRectF(QPointF(0, 0), event.size()))
        self.chart.resize(event.size())
        x, y = self.scene().sceneRect().bottomRight().toTuple()
        self.delta.setPos(x - 100, y - 100)
        super().resizeEvent(event)

    def wave_point_selected(self, point):
        if len(self.callouts) <= 1:
            self.callouts.append(self.tooltip)
        elif len(self.callouts) == 2:
            self.scene().removeItem(self.callouts.pop(0))
            self.callouts.append(self.tooltip)
        else:
            pass

        if len(self.callouts) == 2:
            self.set_delta()

        self.tooltip = Callout(self.chart)

    def set_delta(self):
        x0, y0 = self.callouts[0].x, self.callouts[0].y
        x1, y1 = self.callouts[1].x, self.callouts[1].y
        delta_x = x1 - x0
        delta_y = y1 - y0
        self.delta.setHtml(f'<font color="red">Δ</font>X : {delta_x:.3g}<br><font color="red">Δ</font>Y : {delta_y:.3g}')

    def wave_hovered(self, point, state, name=''):
        if not state:
            self.tooltip.hide()
            return
        x = point.x()
        y = point.y()
        self.tooltip.x = x
        self.tooltip.y = y
        self.tooltip.set_text("{}\nX: {:.3g} \nY: {:.3g} ".format(name, x, y))
        self.tooltip.set_anchor(point)
        self.tooltip.setZValue(11)
        self.tooltip.update_geometry()
        self.tooltip.show()

    def contextMenuEvent(self, event):
        cur = self.wavWin.listView.currentItem()
        if cur is None:
            return
        menu = QMenu(self)
        menu.setStyleSheet('QMenu{menu-scrollable: 1;}')
        actions=[]
        for name in self.wavWin.sigNames[1:]:
            if name == cur.text():
                continue
            action = WaveAction(self, text=name)
            if name in self.wavWin.name2names[cur.text()]:
                font = QFont()
                font.setBold(True)
                action.setFont(font)
            action.triggered.connect(action.act)
            actions.append(action)
        menu.addActions(actions)
        menu.exec(event.globalPos())

    def setAxesTitles(self):
        simType = self.wavWin.simType
        if simType.startswith('ac'):
            xTitle = 'Frequency (Hz)'
        elif simType.startswith('tran'):
            xTitle = 'Time (s)'
        elif simType.startswith('dc'):
            xTitle = self.wavWin.sigNames[0]

        yTitle = ''
        for series in self.chart.series():
            if series.name().startswith('V'):
                if len(yTitle) == 0:
                    yTitle = 'Value (V)'
                elif ' (V)' not in yTitle:
                    yTitle += ' (V)'
            elif series.name().startswith('I'):
                if len(yTitle) == 0:
                    yTitle = 'Value (A)'
                elif ' (A)' not in yTitle:
                    yTitle += ' (A)'

        self.axisX.setTitleText(xTitle)
        self.axisY.setTitleText(yTitle)

    def wheelEvent(self, event) -> None:
        delta = event.angleDelta().y() / 120
        factor = 1.2 ** delta
        self.scale(factor, factor)
        event.accept()
        return super().wheelEvent(event)


class Callout(QGraphicsItem):

    def __init__(self, chart):
        super().__init__(chart)
        self._chart = chart
        self._text = ""
        self._textRect = QRectF()
        self._anchor = QPointF()
        self._font = QFont()
        self._rect = QRectF()
        self.x = None
        self.y = None

    def boundingRect(self):
        anchor = self.mapFromParent(self._chart.mapToPosition(self._anchor))
        rect = QRectF()
        rect.setLeft(min(self._rect.left(), anchor.x()))
        rect.setRight(max(self._rect.right(), anchor.x()))
        rect.setTop(min(self._rect.top(), anchor.y()))
        rect.setBottom(max(self._rect.bottom(), anchor.y()))

        return rect

    def paint(self, painter, option, widget):
        path = QPainterPath()
        path.addRoundedRect(self._rect, 5, 5)
        anchor = self.mapFromParent(self._chart.mapToPosition(self._anchor))
        if not self._rect.contains(anchor) and not self._anchor.isNull():
            point1 = QPointF()
            point2 = QPointF()

            # establish the position of the anchor point in relation to _rect
            above = anchor.y() <= self._rect.top()
            above_center = (anchor.y() > self._rect.top() and
                            anchor.y() <= self._rect.center().y())
            below_center = (anchor.y() > self._rect.center().y() and
                            anchor.y() <= self._rect.bottom())
            below = anchor.y() > self._rect.bottom()

            on_left = anchor.x() <= self._rect.left()
            left_of_center = (anchor.x() > self._rect.left() and
                              anchor.x() <= self._rect.center().x())
            right_of_center = (anchor.x() > self._rect.center().x() and
                               anchor.x() <= self._rect.right())
            on_right = anchor.x() > self._rect.right()

            # get the nearest _rect corner.
            x = (on_right + right_of_center) * self._rect.width()
            y = (below + below_center) * self._rect.height()
            corner_case = ((above and on_left) or (above and on_right) or
                           (below and on_left) or (below and on_right))
            vertical = abs(anchor.x() - x) > abs(anchor.y() - y)

            x1 = (x + left_of_center * 10 - right_of_center * 20 + corner_case *
                  int(not vertical) * (on_left * 10 - on_right * 20))
            y1 = (y + above_center * 10 - below_center * 20 + corner_case *
                  vertical * (above * 10 - below * 20))
            point1.setX(x1)
            point1.setY(y1)

            x2 = (x + left_of_center * 20 - right_of_center * 10 + corner_case *
                  int(not vertical) * (on_left * 20 - on_right * 10))
            y2 = (y + above_center * 20 - below_center * 10 + corner_case *
                  vertical * (above * 20 - below * 10))
            point2.setX(x2)
            point2.setY(y2)

            path.moveTo(point1)
            path.lineTo(anchor)
            path.lineTo(point2)
            path = path.simplified()

        painter.setBrush(QColor(255, 255, 255))
        painter.drawPath(path)
        painter.drawText(self._textRect, self._text)

    def mousePressEvent(self, event):
        event.setAccepted(True)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.setPos(self.mapToParent(
                event.pos() - event.buttonDownPos(Qt.LeftButton)))
            event.setAccepted(True)
        else:
            event.setAccepted(False)

    def set_text(self, text):
        self._text = text
        metrics = QFontMetrics(self._font)
        self._textRect = QRectF(metrics.boundingRect(
            QRect(0.0, 0.0, 150.0, 150.0), Qt.AlignLeft, self._text))
        self._textRect.translate(5, 5)
        self.prepareGeometryChange()
        self._rect = self._textRect.adjusted(-5, -5, 5, 5)


    def set_anchor(self, point):
        self._anchor = QPointF(point)

    def update_geometry(self):
        self.prepareGeometryChange()
        self.setPos(self._chart.mapToPosition(
            self._anchor) + QPointF(10, -50))


class WaveListWidget(QListWidget):
    def __init__(self, wavWin):
        super().__init__()
        self.wavWin = wavWin

    def contextMenuEvent(self, event):
        pass
        
class WaveMenu(QMenu):
    def __int__(self):
        super().__int__()
        

class WaveAction(QAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def act(self) -> None:
        waveform = self.parent().wavWin
        cur = waveform.listView.currentItem()
        if self.font().bold():
            waveform.name2names[cur.text()].remove(self.text())
            font = QFont()
            font.setBold(False)
            self.setFont(font)
        else:
            waveform.name2names[cur.text()].add(self.text())
            font = QFont()
            font.setBold(True)
            self.setFont(font)

        if len(waveform.name2names) > 0:
            font = QFont()
            font.setBold(True)
            cur.setFont(font)
        else:
            font = QFont
            font.setBold(False)
            cur.setFont(font)

        waveform.chartView.draw(cur.text(), *waveform.name2names[cur.text()])


class WaveTextItem(QGraphicsTextItem):
    def mouseDoubleClickEvent(self, event):
        self.parentItem().scene().views()[0].showCalculator()
