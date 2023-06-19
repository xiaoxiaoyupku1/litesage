import re
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, 
    QDialogButtonBox, QVBoxLayout,
    QFileDialog
)

class ParameterDialog(QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Paramters")
        formLayout = QFormLayout()
        text = item.toPlainText()
        currentName, currentValue = re.split('\s+', text.strip())
        self.name = QLineEdit(currentName)
        self.value = QLineEdit(currentValue)
        formLayout.addRow("Name:", self.name)
        formLayout.addRow("Value:", self.value)
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