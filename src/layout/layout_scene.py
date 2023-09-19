from PySide6.QtWidgets import QGraphicsScene


class LayoutScene(QGraphicsScene):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)