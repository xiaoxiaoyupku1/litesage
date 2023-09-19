import sys
from PySide6.QtWidgets import QApplication
from src.eda import FoohuEda
from src.layout.manage import LayoutApplication

app = QApplication(sys.argv)
eda = FoohuEda()
layout = LayoutApplication()
eda.actOpenFLayout.triggered.connect(layout.open)
eda.show()
app.exec()