import sys
from PySide6.QtWidgets import QApplication
from src.eda import FoohuEda

app = QApplication(sys.argv)
eda = FoohuEda(app)
eda.show()
app.exec()