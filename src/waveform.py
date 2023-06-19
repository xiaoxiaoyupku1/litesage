from numpy import array as NDArray
from PySide6.QtGui import (QPainter)
from PySide6.QtWidgets import (QWidget, QListWidget, QGridLayout, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsTextItem)
from PySide6.QtCharts import (QChart, QLineSeries)
from PySide6.QtCore import Qt, QPointF, QRectF, QRect
from PySide6.QtGui import QPainter, QFont, QFontMetrics, QPainterPath, QColor
from src.wavefile.wavefile import getWaveFileHandler


class FoohuEdaWaveWindow(QWidget):
    def __init__(self, schWin, waveFile):
        super().__init__()

        self.waveFile = waveFile
        self.sigNames = None
        self.sigValues = None
        self.listView = None
        self.chartView = None # wave signal chart
        self.layout = None  # window layout of widgets

        self.parseWaveFile()
        self.setupUi()

        self.schWin = schWin  # FoohuEda schematic window
        # TODO: make self an embedded window instead of an independent window
        #       embedded to its parent which is schWin (FoohuEda)
        self.setWindowTitle('FOOHU EDA - Waveform Viewer')
        self.resize(900, 500)

        self.setLayout(self.layout)
        self.show()

    def parseWaveFile(self):
        handler = getWaveFileHandler(self.waveFile)
        handler.parseWaveFile()

        self.sigNames = handler.getSigNames()
        self.sigValues = handler.getSigVals('tr')

    def setupUi(self):
        # Left side: wave name list
        self.listView = QListWidget()
        self.listView.addItems(self.sigNames[1:])
        self.listView.currentItemChanged.connect(self.change_wave)

        # Right side: wave signal chart
        self.chartView = ChartView()

        # Layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.listView, 1, 0)
        self.layout.setColumnStretch(0, 0)
        self.layout.addWidget(self.chartView, 1, 1)
        self.layout.setColumnStretch(1, 1)

        # Select 1st wave
        self.change_wave(None, sigName=self.sigNames[1])

    def change_wave(self, selItem, sigName=None):
        if sigName is None or not isinstance(sigName, str):
            sigName = selItem.text()
        index = self.sigNames.index(sigName)
        self.series = QLineSeries()
        self.series.appendNp(NDArray(self.sigValues[0])*1e3,
                             NDArray(self.sigValues[index]))
        self.series.doubleClicked.connect(self.chartView.wave_clicked)
        self.series.hovered.connect(self.chartView.wave_hovered)
        self.chartView.chart.removeAllSeries()
        self.chartView.chart.addSeries(self.series)
        self.chartView.chart.setTitle(sigName)
        self.chartView.chart.createDefaultAxes()
        self.chartView.chart.axes()[0].setTitleText("Time")
        self.chartView.chart.axes()[1].setTitleText("Value")

        for callout in self.chartView.callouts:
            self.chartView.scene().removeItem(callout)
        self.chartView.callouts = []
        self.chartView.tooltip.hide()
        self.chartView.delta.setHtml("")

class ChartView(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setScene(QGraphicsScene(self))

        self.chart = QChart()
        self.chart.setMinimumSize(640, 480)
        self.chart.legend().hide()
        self.chart.setAcceptHoverEvents(True)
        self.scene().addItem(self.chart)

        self.delta = QGraphicsTextItem(self.chart)
        x, y = self.scene().sceneRect().bottomRight().toTuple()
        self.delta.setPos(x - 100, y - 100)
        self.delta.setZValue(15)

        self.setRenderHint(QPainter.Antialiasing)

        self.tooltip = Callout(self.chart)
        self.callouts = []

    def resizeEvent(self, event):
        self.scene().setSceneRect(QRectF(QPointF(0, 0), event.size()))
        self.chart.resize(event.size())
        x, y = self.scene().sceneRect().bottomRight().toTuple()
        self.delta.setPos(x - 100, y - 100)
        QGraphicsView.resizeEvent(self, event)

    def wave_clicked(self, point):
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
        self.delta.setHtml(f'<font color="red">Δ</font>X : {delta_x:.4f}<br><font color="red">Δ</font>Y : {delta_y:.4f}')

    def wave_hovered(self, point, state):
        if self.tooltip == 0:
            self.tooltip = Callout(self.chart)

        if state:
            x = point.x()
            y = point.y()
            self.tooltip.x = x
            self.tooltip.y = y
            self.tooltip.set_text(f"X: {x:.4f} \nY: {y:.4f} ")
            self.tooltip.set_anchor(point)
            self.tooltip.setZValue(11)
            self.tooltip.update_geometry()
            self.tooltip.show()
        else:
            self.tooltip.hide()


class Callout(QGraphicsItem):

    def __init__(self, chart):
        QGraphicsItem.__init__(self, chart)
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
