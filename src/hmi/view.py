from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGraphicsView)

class SchView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.origScale = 1.25
        self.scale(self.origScale**3, self.origScale**3)

    def wheelEvent(self, event) -> None:
        # Only zoom/dezoom if CTRL is pressed
        if event.modifiers() == Qt.ControlModifier:
            zoomInFactor = self.origScale
            zoomOutFactor = 1 / zoomInFactor

            # Save the scene pos
            oldPos = event.scenePosition()

            # Zoom
            if event.angleDelta().y() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale(zoomFactor, zoomFactor)

            # Get the new position
            newPos = event.scenePosition()

            # Move scene to old position
            delta = newPos - oldPos
            self.translate(delta.x(), delta.y())
        # Move scrollbar
        else:
            super().wheelEvent(event)

        self.update()

    def fit(self, scene):
        self.fitInView(scene.itemsBoundingRect(), Qt.KeepAspectRatio)