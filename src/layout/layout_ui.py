# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'layout_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QDockWidget, QFrame, QGraphicsView,
    QHBoxLayout, QLabel, QListView, QMainWindow,
    QMenu, QMenuBar, QSizePolicy, QSpacerItem,
    QStatusBar, QToolBar, QVBoxLayout, QWidget)
from src.layout import logo_resource_rc
from src.layout.layout_view import LayoutView
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1087, 722)
        MainWindow.setAutoFillBackground(False)
        self.actionopen = QAction(MainWindow)
        self.actionopen.setObjectName(u"actionopen")
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionOpen.setIconVisibleInMenu(True)
        self.actionOpen.setShortcutVisibleInContextMenu(True)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave_As = QAction(MainWindow)
        self.actionSave_As.setObjectName(u"actionSave_As")
        self.actionExport = QAction(MainWindow)
        self.actionExport.setObjectName(u"actionExport")
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionMove = QAction(MainWindow)
        self.actionMove.setObjectName(u"actionMove")
        self.actionPath = QAction(MainWindow)
        self.actionPath.setObjectName(u"actionPath")
        self.actionDele = QAction(MainWindow)
        self.actionDele.setObjectName(u"actionDele")
        self.actionVia = QAction(MainWindow)
        self.actionVia.setObjectName(u"actionVia")
        self.actionRuler = QAction(MainWindow)
        self.actionRuler.setObjectName(u"actionRuler")
        self.actionUpload = QAction(MainWindow)
        self.actionUpload.setObjectName(u"actionUpload")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.graphicsView = LayoutView(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout.addWidget(self.graphicsView)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.labelFoohuPower = QLabel(self.frame)
        self.labelFoohuPower.setObjectName(u"labelFoohuPower")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelFoohuPower.sizePolicy().hasHeightForWidth())
        self.labelFoohuPower.setSizePolicy(sizePolicy)
        self.labelFoohuPower.setMinimumSize(QSize(108, 20))
        self.labelFoohuPower.setMaximumSize(QSize(108, 20))
        self.labelFoohuPower.setStyleSheet(u"border-image: url(:/logo/poweredBy.png);")
        self.labelFoohuPower.setPixmap(QPixmap(u"../../../../poweredBy.png"))
        self.labelFoohuPower.setScaledContents(True)
        self.labelFoohuPower.setWordWrap(False)

        self.horizontalLayout.addWidget(self.labelFoohuPower)


        self.verticalLayout.addWidget(self.frame)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1087, 22))
        self.menu_2 = QMenu(self.menubar)
        self.menu_2.setObjectName(u"menu_2")
        self.menuAction = QMenu(self.menubar)
        self.menuAction.setObjectName(u"menuAction")
        MainWindow.setMenuBar(self.menubar)
        self.Windowlayer = QDockWidget(MainWindow)
        self.Windowlayer.setObjectName(u"Windowlayer")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.Windowlayer.sizePolicy().hasHeightForWidth())
        self.Windowlayer.setSizePolicy(sizePolicy1)
        self.Windowlayer.setMinimumSize(QSize(144, 114))
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.horizontalLayout_2 = QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.listViewLayers = QListView(self.dockWidgetContents)
        self.listViewLayers.setObjectName(u"listViewLayers")
        sizePolicy1.setHeightForWidth(self.listViewLayers.sizePolicy().hasHeightForWidth())
        self.listViewLayers.setSizePolicy(sizePolicy1)
        self.listViewLayers.setResizeMode(QListView.Adjust)
        self.listViewLayers.setWordWrap(True)

        self.horizontalLayout_2.addWidget(self.listViewLayers)

        self.Windowlayer.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.Windowlayer)
        self.WindowNet = QDockWidget(MainWindow)
        self.WindowNet.setObjectName(u"WindowNet")
        self.WindowNet.setMinimumSize(QSize(144, 114))
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.horizontalLayout_8 = QHBoxLayout(self.dockWidgetContents_2)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.listViewNets = QListView(self.dockWidgetContents_2)
        self.listViewNets.setObjectName(u"listViewNets")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.listViewNets.sizePolicy().hasHeightForWidth())
        self.listViewNets.setSizePolicy(sizePolicy2)
        self.listViewNets.setResizeMode(QListView.Adjust)

        self.horizontalLayout_8.addWidget(self.listViewNets)

        self.WindowNet.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.WindowNet)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menuAction.menuAction())
        self.menu_2.addAction(self.actionOpen)
        self.menu_2.addAction(self.actionSave)
        self.menu_2.addAction(self.actionSave_As)
        self.menu_2.addAction(self.actionExport)
        self.menu_2.addAction(self.actionUpload)
        self.menu_2.addAction(self.actionClose)
        self.menuAction.addAction(self.actionMove)
        self.menuAction.addAction(self.actionPath)
        self.menuAction.addAction(self.actionDele)
        self.menuAction.addAction(self.actionVia)
        self.menuAction.addAction(self.actionRuler)
        self.toolBar.addAction(self.actionMove)
        self.toolBar.addAction(self.actionPath)
        self.toolBar.addAction(self.actionDele)
        self.toolBar.addAction(self.actionVia)
        self.toolBar.addAction(self.actionRuler)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Foohu Technology", None))
        self.actionopen.setText(QCoreApplication.translate("MainWindow", u"open", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionSave_As.setText(QCoreApplication.translate("MainWindow", u"Save As", None))
        self.actionExport.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionMove.setText(QCoreApplication.translate("MainWindow", u"Move", None))
        self.actionPath.setText(QCoreApplication.translate("MainWindow", u"Path", None))
        self.actionDele.setText(QCoreApplication.translate("MainWindow", u"Dele", None))
        self.actionVia.setText(QCoreApplication.translate("MainWindow", u"Via", None))
        self.actionRuler.setText(QCoreApplication.translate("MainWindow", u"Ruler", None))
        self.actionUpload.setText(QCoreApplication.translate("MainWindow", u"Upload", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"XY:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"10000   10000", None))
        self.labelFoohuPower.setText("")
        self.menu_2.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuAction.setTitle(QCoreApplication.translate("MainWindow", u"Action", None))
#if QT_CONFIG(whatsthis)
        self.Windowlayer.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(accessibility)
        self.Windowlayer.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.Windowlayer.setWindowTitle(QCoreApplication.translate("MainWindow", u"Layers", None))
        self.WindowNet.setWindowTitle(QCoreApplication.translate("MainWindow", u"Nets", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

