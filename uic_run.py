import sys
from PySide6 import QtWidgets
import PySide6.QtGui


from uic import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

    def mousePressEvent_bk(self, event) -> None:
        if self.symbol == 'R':
            self.painR(event.position())


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()