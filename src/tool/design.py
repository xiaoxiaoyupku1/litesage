import re
from PySide6.QtCore import (Qt)
from src.hmi.line import Line
from src.hmi.rect import Rect
from src.hmi.polygon import Polygon
from src.hmi.ellipse import Circle
from src.hmi.text import ParameterText


def dumpDesign(filePath, rectItem):
    shapes = rectItem.collidingItems()
    rect = rectItem.rect()
    rectW = rect.width()
    rectH = rect.height()
    rectX = rect.x()
    rectY = rect.y()
    centerX = rectX + rectW / 2
    centerY = rectY + rectH / 2

    with open(filePath, 'w') as f:
        # rect of design
        f.write('RECT:')
        items = [str(num) for num in [rectX - centerX,
                                      rectY - centerY,
                                      rectW,
                                      rectH]]
        f.write(','.join(items))
        f.write('\n')

        for shape in shapes:
            if isinstance(shape, Line):
                # wire
                if shape.pen().color() == Qt.blue:
                    line = shape.line()
                    f.write('Wire:')
                    items = [str(num) for num in [line.x1() - centerX,
                                                  line.y1() - centerY,
                                                  line.x2() - centerX,
                                                  line.y2() - centerY]]
                    f.write(','.join(items))
                    f.write('\n')

                # line of symbol
                else:
                    shapeX = shape.pos().x()
                    shapeY = shape.pos().y()
                    line = shape.line()
                    f.write('Line:')
                    items = [str(num) for num in [line.x1() + shapeX - centerX, 
                                                  line.y1() + shapeY - centerY, 
                                                  line.x2() + shapeX - centerX, 
                                                  line.y2() + shapeY - centerY]]
                    f.write(','.join(items))
                    f.write('\n')

            # rect of symbol
            elif isinstance(shape, Rect):
                shapeX = shape.pos().x()
                shapeY = shape.pos().y()
                shapeRectX = shape.rect().x()
                shapeRectY = shape.rect().y()
                shapeRectW = shape.rect().width()
                shapeRectH = shape.rect().height()

                f.write('Rect:')
                items = [str(num) for num in [shapeRectX + shapeX - centerX,
                                              shapeRectY + shapeY - centerY,
                                              shapeRectW,
                                              shapeRectH]]
                f.write(','.join(items))
                f.write('\n')

            # polygon/pin
            elif isinstance(shape, Polygon):
                if shape.pen().color() == Qt.red:
                    f.write('Pin:') 
                else:
                    f.write('Polygon:')
                shapeX = shape.pos().x()
                shapeY = shape.pos().y()
                items = []
                for point in shape.polygon().toList():
                    pointStr = '{},{}'.format(
                        str(point.x() + shapeX - centerX),
                        str(point.y() + shapeY - centerY)
                    )
                    items.append(pointStr)
                f.write(';'.join(items))
                f.write('\n')

            # circle
            elif isinstance(shape, Circle):
                shapeX = shape.x()
                shapeY = shape.y()
                shapeRectX = shape.rect().x()
                shapeRectY = shape.rect().y()
                shapeRectW = shape.rect().width()
                shapeRectH = shape.rect().height()
                f.write('Circle:')
                items = [str(num) for num in [shapeRectX + shapeX - centerX,
                                              shapeRectY + shapeY - centerY,
                                              shapeRectW,
                                              shapeRectH]]
                f.write(','.join(items))
                f.write('\n')

            # parameter text
            elif isinstance(shape, ParameterText):
                text = shape.toPlainText()
                currentName, currentValue = re.split('\s+', text.strip())
                f.write('Parameter:')
                items = [str(n) for n in [currentName,
                                          currentValue,
                                          shape.x() - centerX,
                                          shape.y() - centerY]]
                f.write(','.join(items))
                f.write('\n')