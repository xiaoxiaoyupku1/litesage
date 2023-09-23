import sys
from PySide6.QtWidgets import QApplication
from src.eda import FoohuEda
from src.layout.layout_main_window import LayoutMainWindow

app = QApplication(sys.argv)
eda = FoohuEda()
layout_app = LayoutMainWindow(app, eda)
eda.actOpenFLayout.triggered.connect(layout_app.show)
eda.show()
app.exec()