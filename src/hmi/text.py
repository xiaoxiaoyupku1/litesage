from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsTextItem, QTextBrowser,QGraphicsItem

class Text(QGraphicsTextItem):
    def __init__(self, text='', posx=0, posy=0, orient='0', dimension=62.5):
        super().__init__(text)
        self.setPos(posx, posy - dimension)
        self.setDefaultTextColor('black')
        font = self.font()
        font.setPixelSize(dimension)
        self.setFont(font)


class ParameterText(QGraphicsTextItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.posx = 0
        self.posy = 0

class WireNameText(ParameterText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)



class NetlistText(QTextBrowser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLineWrapMode(QTextBrowser.NoWrap)