from numpy import array as NDArray
from PySide6.QtGui import (QPainter)
from PySide6.QtWidgets import (QWidget, QListWidget, QGridLayout)
from PySide6.QtCharts import (QChart, QChartView, QLineSeries)
from src.wavefile.wavefile import getWaveFileHandler

class FoohuEdaWaveWindow(QWidget):
    def __init__(self, schWin, waveFile):
        super().__init__()

        self.waveFile = waveFile
        self.sigNames = None
        self.sigValues = None
        self.listView = None
        self.chartView = None
        self.chart = None           # wave signal chart
        self.layout = None          # window layout of widgets

        self.parseWaveFile()
        self.setupUi()

        self.schWin = schWin        # FoohuEda schematic window
        # TODO: make self an embedded window instead of an independent window
        #       embedded to its parent which is schWin (FoohuEda)
        self.setWindowTitle('FOOHU EDA - Waveform Viewer')
        self.resize(900, 500)

        self.setLayout(self.layout)
        self.show()

    def parseWaveFile(self):
        handler  = getWaveFileHandler(self.waveFile)
        handler.parseWaveFile()

        self.sigNames = handler.getSigNames()
        self.sigValues = handler.getSigVals('tr')

    def setupUi(self):
        # Left side: wave name list
        self.listView = QListWidget()
        self.listView.addItems(self.sigNames[1:])
        self.listView.currentItemChanged.connect(self.changeWave)

        # Right side: wave signal chart
        self.chart = QChart()
        self.chart.legend().hide()
        self.chartView = QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.chartView.setRubberBand(QChartView.RectangleRubberBand)

        # Layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.listView, 1, 0)
        self.layout.setColumnStretch(0, 0)
        self.layout.addWidget(self.chartView, 1, 1)
        self.layout.setColumnStretch(1, 1)

        # Select 1st wave
        self.changeWave(None, sigName=self.sigNames[1])

    def changeWave(self, selItem, sigName=None):
        if sigName is None or not isinstance(sigName, str):
            sigName = selItem.text()
        index = self.sigNames.index(sigName)
        series = QLineSeries()
        series.appendNp(NDArray(self.sigValues[0]),
                        NDArray(self.sigValues[index]))
        self.chart.removeAllSeries()
        self.chart.addSeries(series)
        self.chart.setTitle(sigName)
        self.chart.createDefaultAxes()