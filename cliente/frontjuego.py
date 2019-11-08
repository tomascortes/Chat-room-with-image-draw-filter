"""
codigo obtenido de
ZetCode PyQt5 tutorial
https://stackoverflow.com/questions/14101297/qt-beginner-qpainter-and-qrect
"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QPushButton, QScrollArea, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.Qt import QColor
import sys
import threading as th
import socket
import json
from PyQt5.QtWidgets import QApplication
from datetime import datetime
from PyQt5 import uic, QtGui
from PyQt5.QtGui import QPixmap, QTransform, QFont, QPainter
import sip
from parametros import N, M, PX
from PyQt5.QtWidgets import QApplication

class Juego(QWidget):
    '''Esta clase se cre+o para posicionar todos los elementos
    en la ventana principal de juego, no se utilizó PyQt, para
     manejar algunas cosas que de mejor forma, como el mapa
    y la posicion de los elementos
    '''
    inicio = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.matriz = []
        self.inicio.connect(self.show)

        for i in range(N):
            self.matriz.append([])
            for j in range(M):
                if j != M - 1 :
                    rec2 = VRect(self)
                    rec2.setGeometry(i * PX*2 + PX//2, j * PX*2 + PX, PX*2, PX*2)

                if i!= N - 1 :
                    rec = HRect(self)
                    rec.setGeometry(i * PX*2 + PX, j * PX*2 + PX/2, PX*2, PX*2)
                dot = Punto(self)
                dot.setGeometry(i * PX*2 , j * PX*2, PX*2, PX*2)
                self.matriz[i].append(rec)

        font = QFont()
        font.setPointSize(N//5)


class Punto(QLabel):

    def __init__(self, parent):
        super().__init__(parent)
        self.show()
        self.setMinimumSize(PX, PX)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QColor(Qt.black))
        qp.setBrush(QColor(Qt.black))
        qp.drawEllipse(0, 0, PX, PX)
        qp.end()



class HRect(QLabel):

    def __init__(self, parent):
        super().__init__(parent)
        self.show()
        self.setMinimumSize(PX, PX)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QColor(Qt.black))
        qp.setBrush(QColor(Qt.black))
        qp.drawRect(0, 0, PX, PX//5)
        qp.end()

    def mousePressEvent(self, event):
        print('owooo')
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            print('holaa')


class VRect(QLabel):

    def __init__(self, parent):
        super().__init__(parent)
        self.show()
        self.setMinimumSize(PX, PX)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QColor(Qt.black))
        qp.setBrush(QColor(Qt.black))
        qp.drawRect(0, 0, PX//5, PX)
        qp.end()

    def mousePressEvent(self, event):
        print('asjfdnf')
        if event.button() == Qt.LeftButton:
            print('fui apretado')



if __name__ == "__main__":
    app = QApplication([])
    cliente = Juego()
    cliente.show()
    sys.exit(app.exec_())
