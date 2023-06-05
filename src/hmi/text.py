from PySide6.QtWidgets import QGraphicsTextItem
from src.hmi.dialog import ParameterDialog

class ParameterText(QGraphicsTextItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.posx = 0
        self.posy = 0

    def contextMenuEvent(self, event):
        dialog = ParameterDialog(parent=None, item=self)
        if dialog.exec():
            text = '    {}\n\n    {}'.format(dialog.name.text(), 
                                             dialog.value.text())
            self.setPlainText(text)
        return super().contextMenuEvent(event)