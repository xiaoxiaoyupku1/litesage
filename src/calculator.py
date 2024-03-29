
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont




class Calculator(QWidget):
    def __init__(self, X1,Y1,X2,Y2):
        super().__init__()

        self.X1 = X1
        self.Y1 = Y1
        self.X2 = X2
        self.Y2 = Y2

        self.prev_button = None

        self.setWindowTitle("Calculator")
        #self.setFixedSize(400, 400)
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.num_grid = NumGrid()
        self.math_str = ''
        self.main_ind = Indicator(self.math_str)

        self.main_layout.addWidget(self.main_ind)
        self.main_layout.addWidget(self.num_grid)
        self.setLayout(self.main_layout)


class StdButton(QWidget):
    def __init__(self, text, parent=None):
        super(StdButton, self).__init__(parent)
        self.setMaximumWidth(200)
        self.button = QPushButton()
        self.button.setText(text)
        self.column_layout = QVBoxLayout()
        self.column_layout.addWidget(self.button)
        self.setLayout(self.column_layout)
        self.button.clicked.connect(self.handle_click)

    def cal(self):
        return self.parent().parent()

    def clear_ind(self):
        self.cal().math_str = ''
        self.cal().main_ind.label.setText(self.cal().math_str)
        self.cal().main_ind.need_clear = False

    def handle_click(self):
        main_ind = self.cal().main_ind
        txt = self.button.text()

        if txt == 'C':
            self.clear_ind()
            return

        elif txt == '=':
            expr = self.cal().math_str
            try:
                res = str(eval(expr)) if len(expr) > 0 else ''
            except:
                res = 'Wrong input. Press "C".'
            self.cal().math_str = res
            main_ind.label.setText(res)
            main_ind.need_clear = True
            return

        if main_ind.need_clear:
            self.clear_ind()

        if txt in ('X1', 'X2', 'Y1', 'Y2'):
            txt = getattr(self.cal(), txt)
            txtstr = str(txt)
            if txtstr.startswith('(') and txtstr.endswith(')'):
                pass
            else:
                txt = f'({txt:.3g})'

        elif txt in ('+', '-', '*', '/'):
            expr = self.cal().math_str
            if expr.startswith('(') and expr.endswith(')'):
                pass
            elif len(expr) > 0:
                expr = f'({expr})'
            self.cal().math_str = expr
            main_ind.label.setText(expr)

        self.cal().math_str += txt
        main_ind.label.setText(self.cal().math_str)


class NumGrid(QWidget):
    def __init__(self, parent=None):
        super(NumGrid, self).__init__(parent)

        self.num_grid = QGridLayout()

        self.x1 = StdButton('X1')
        self.y1 = StdButton('Y1')
        self.x2 = StdButton('X2')
        self.y2 = StdButton('Y2')
        self.num_grid.addWidget(self.x1, 0, 1)
        self.num_grid.addWidget(self.y1, 0, 2)
        self.num_grid.addWidget(self.x2, 0, 3)
        self.num_grid.addWidget(self.y2, 0, 4)
        count = 9
        for x in range(2, 5, 1):
            for y in range(3, 0, -1):
                button = StdButton(str(count))
                self.num_grid.addWidget(button, x, y)
                count = count - 1

        self.button_neg = StdButton("00")
        self.button0 = StdButton("0")
        self.button_dec = StdButton(".")

        self.button_c = StdButton("C")

        self.button_d = StdButton("/")
        self.button_m = StdButton("*")
        self.button_s = StdButton("-")
        self.button_a = StdButton("+")
        self.button_e = StdButton("=")

        self.num_grid.addWidget(self.button_neg, 5, 1)
        self.num_grid.addWidget(self.button0, 5, 2)
        self.num_grid.addWidget(self.button_dec, 5, 3)

        self.num_grid.addWidget(self.button_c, 1, 1)

        self.num_grid.addWidget(self.button_d, 1, 4)
        self.num_grid.addWidget(self.button_m, 2, 4)
        self.num_grid.addWidget(self.button_s, 3, 4)
        self.num_grid.addWidget(self.button_a, 4, 4)
        self.num_grid.addWidget(self.button_e, 5, 4)

        self.setLayout(self.num_grid)

class Indicator(QWidget):
    def __init__(self, text, parent=None):
        super(Indicator, self).__init__(parent)
        self.label = QLabel()
        self.label.setText(text)
        self.label.setFixedWidth(340)
        self.label.setFont(QFont('Roboto', 20))
        self.label.setAlignment(Qt.AlignRight)
        self.label.setStyleSheet('border: 4px solid grey;')
        self.column_layout = QVBoxLayout()
        self.column_layout.setAlignment(Qt.AlignCenter)
        self.column_layout.addWidget(self.label)
        self.setLayout(self.column_layout)
        self.need_clear = False