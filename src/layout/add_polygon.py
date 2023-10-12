# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_polygon.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 300)
        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(107, 93, 215, 132))
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_line_width = QLabel(self.widget)
        self.label_line_width.setObjectName(u"label_line_width")

        self.gridLayout.addWidget(self.label_line_width, 0, 0, 1, 1)

        self.lineEditLineWidth = QLineEdit(self.widget)
        self.lineEditLineWidth.setObjectName(u"lineEditLineWidth")

        self.gridLayout.addWidget(self.lineEditLineWidth, 0, 1, 1, 1)

        self.label_Layer_id = QLabel(self.widget)
        self.label_Layer_id.setObjectName(u"label_Layer_id")

        self.gridLayout.addWidget(self.label_Layer_id, 1, 0, 1, 1)

        self.lineEditLayId = QLineEdit(self.widget)
        self.lineEditLayId.setObjectName(u"lineEditLayId")

        self.gridLayout.addWidget(self.lineEditLayId, 1, 1, 1, 1)

        self.label_net_name = QLabel(self.widget)
        self.label_net_name.setObjectName(u"label_net_name")

        self.gridLayout.addWidget(self.label_net_name, 2, 0, 1, 1)

        self.lineEditNetName = QLineEdit(self.widget)
        self.lineEditNetName.setObjectName(u"lineEditNetName")

        self.gridLayout.addWidget(self.lineEditNetName, 2, 1, 1, 1)

        self.label_add_net_text = QLabel(self.widget)
        self.label_add_net_text.setObjectName(u"label_add_net_text")

        self.gridLayout.addWidget(self.label_add_net_text, 3, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.radioButton_yes = QRadioButton(self.widget)
        self.radioButton_yes.setObjectName(u"radioButton_yes")

        self.horizontalLayout.addWidget(self.radioButton_yes)

        self.radioButton_no = QRadioButton(self.widget)
        self.radioButton_no.setObjectName(u"radioButton_no")

        self.horizontalLayout.addWidget(self.radioButton_no)


        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 1)

        self.pushButtonConfirm = QPushButton(self.widget)
        self.pushButtonConfirm.setObjectName(u"pushButtonConfirm")

        self.gridLayout.addWidget(self.pushButtonConfirm, 4, 0, 1, 1)

        self.pushButtonCancel = QPushButton(self.widget)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")

        self.gridLayout.addWidget(self.pushButtonCancel, 4, 1, 1, 1)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_line_width.setText(QCoreApplication.translate("Dialog", u"Line Width", None))
        self.label_Layer_id.setText(QCoreApplication.translate("Dialog", u"Layer Id", None))
        self.label_net_name.setText(QCoreApplication.translate("Dialog", u"Net Name", None))
        self.label_add_net_text.setText(QCoreApplication.translate("Dialog", u"Add Net Text", None))
        self.radioButton_yes.setText(QCoreApplication.translate("Dialog", u"Yes", None))
        self.radioButton_no.setText(QCoreApplication.translate("Dialog", u"No", None))
        self.pushButtonConfirm.setText(QCoreApplication.translate("Dialog", u"Confirm", None))
        self.pushButtonCancel.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
    # retranslateUi

