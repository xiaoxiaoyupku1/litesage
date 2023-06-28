import re
from PySide6.QtCore import (
    QStringListModel
)
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, 
    QDialogButtonBox, QVBoxLayout,
    QFileDialog, QListView,
)

class ParameterDialog(QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle('Enter Paramters')
        formLayout = QFormLayout()
        text = item.toPlainText()
        currentName, currentValue = re.split('\s+', text.strip())
        self.name = QLineEdit(currentName)
        self.value = QLineEdit(currentValue)
        formLayout.addRow('Name:', self.name)
        formLayout.addRow('Value:', self.value)
        QBtn = QDialogButtonBox()
        QBtn.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        QBtn.accepted.connect(self.accept)
        QBtn.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addWidget(QBtn)
        self.setLayout(layout)


class DesignFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', 'load')       # load or save
        super().__init__(*args, **kwargs)
        self.accepted = QDialog.Accepted

        mimeTypes = ['text/plain']
        self.setMimeTypeFilters(mimeTypes)

        if mode == 'load':
            acceptMode = QFileDialog.AcceptOpen
        else:
            acceptMode = QFileDialog.AcceptSave
        self.setAcceptMode(acceptMode)


class DeviceChoiceDialog(QDialog):
    def __init__(self, parent, title, devices=[]):
        super().__init__(parent)
        self.accepted = QDialog.Accepted
        self.setWindowTitle(title)
        strlist = QStringListModel()
        strlist.setStringList(devices)
        self.listview = QListView()
        self.listview.setModel(strlist)
        QBtn = QDialogButtonBox()
        QBtn.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        QBtn.accepted.connect(self.accept)
        QBtn.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addWidget(self.listview)
        layout.addWidget(QBtn)
        self.setLayout(layout)