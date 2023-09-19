# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'layout.ui'
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
from PySide6.QtWidgets import (QApplication, QDockWidget, QGraphicsView, QHBoxLayout,
    QListView, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QToolBar, QVBoxLayout,
    QWidget)
from src.layout import logo_resource_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1160, 854)
        MainWindow.setAutoFillBackground(False)
        self.actionopen = QAction(MainWindow)
        self.actionopen.setObjectName(u"actionopen")
        self.actionLoad = QAction(MainWindow)
        self.actionLoad.setObjectName(u"actionLoad")
        self.actionLoad.setIconVisibleInMenu(True)
        self.actionLoad.setShortcutVisibleInContextMenu(True)
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
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.graphicsView = QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout.addWidget(self.graphicsView)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setStyleSheet(u"")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1160, 22))
        self.menu_2 = QMenu(self.menubar)
        self.menu_2.setObjectName(u"menu_2")
        self.menuAction = QMenu(self.menubar)
        self.menuAction.setObjectName(u"menuAction")
        MainWindow.setMenuBar(self.menubar)
        self.Windowlayer = QDockWidget(MainWindow)
        self.Windowlayer.setObjectName(u"Windowlayer")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Windowlayer.sizePolicy().hasHeightForWidth())
        self.Windowlayer.setSizePolicy(sizePolicy)
        self.Windowlayer.setMinimumSize(QSize(144, 114))
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.horizontalLayout_2 = QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.listViewLayers = QListView(self.dockWidgetContents)
        self.listViewLayers.setObjectName(u"listViewLayers")
        sizePolicy.setHeightForWidth(self.listViewLayers.sizePolicy().hasHeightForWidth())
        self.listViewLayers.setSizePolicy(sizePolicy)
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
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.listViewNets.sizePolicy().hasHeightForWidth())
        self.listViewNets.setSizePolicy(sizePolicy1)
        self.listViewNets.setResizeMode(QListView.Adjust)

        self.horizontalLayout_8.addWidget(self.listViewNets)

        self.WindowNet.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.WindowNet)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menuAction.menuAction())
        self.menu_2.addAction(self.actionLoad)
        self.menu_2.addAction(self.actionSave)
        self.menu_2.addAction(self.actionSave_As)
        self.menu_2.addAction(self.actionExport)
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
        self.actionLoad.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionSave_As.setText(QCoreApplication.translate("MainWindow", u"Save As", None))
        self.actionExport.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionMove.setText(QCoreApplication.translate("MainWindow", u"Move", None))
        self.actionPath.setText(QCoreApplication.translate("MainWindow", u"Path", None))
        self.actionDele.setText(QCoreApplication.translate("MainWindow", u"Dele", None))
        self.actionVia.setText(QCoreApplication.translate("MainWindow", u"Via", None))
        self.actionRuler.setText(QCoreApplication.translate("MainWindow", u"Ruler", None))
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

