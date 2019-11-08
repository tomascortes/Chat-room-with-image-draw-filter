from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QPushButton, QScrollArea, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextCursor, QIcon
import sys
import threading as th
import socket
import json
from PyQt5.QtWidgets import QApplication
from datetime import datetime
from PyQt5 import uic, QtGui
from PyQt5.QtGui import QPixmap, QTransform, QFont
import sip


window_name, base_class = uic.loadUiType("ui_data/seleccion_sala.ui")
window_name1, base_class1 = uic.loadUiType("ui_data/label_sala.ui")
window_name2, base_class2 = uic.loadUiType("ui_data/ventana_espera.ui")


class Seleccion(window_name, base_class):
    mostrar_sala_selec = pyqtSignal()
    cargar_px = pyqtSignal(bytearray)
    path_obtenido = pyqtSignal(str)
    senal_sala = pyqtSignal()
    sala_aceptada = pyqtSignal(list)
    sala_espera = pyqtSignal(str)
    salir_sala_s2 = pyqtSignal()
    inicio_juego_s = pyqtSignal()
    en_juego_s = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.scrollable = ScrollableSalas()
        self.en_juego_s.connect(self.en_juego)
        self.cargar_img.clicked.connect(self.abrir_foto)
        self.scrollArea.setWidget(self.scrollable)
        self.crear_sala.clicked.connect(self.senal_sala.emit)
        self.ventana_espera = VentanaEspera()
        self.ventana_espera.salir_sala_s1.connect(self.salir_sala)
        self.ventana_espera.inicio_contador_s2.connect(self.inicio_contador)
        self.sala_aceptada.connect(self.scrollable.crear_sala)
        self.cargar_px.connect(self.act_imagen)
        self.mostrar_sala_selec.connect(self.show)
        self.sala_espera.connect(self.open_espera)

        self.contando = QTimer(self)
        self.contando.timeout.connect(self.restar_c)

    def abrir_foto(self):
        self.abridor = SubirFoto(self.path_obtenido)

    def act_imagen(self, data):
        px = QPixmap()
        px.loadFromData(data, '1')
        self.imagen.setPixmap(px.scaled(100, 100))
        self.imagen.resize(120,120)

    def open_espera(self, jefe):
        self.ventana_espera.show()
        self.hide()
        self.ventana_espera.jefe_sala.setText(f'Jefe de sala: {jefe}')

    def salir_sala(self):
        self.show()
        self.salir_sala_s2.emit()

    def inicio_contador(self):
        self.contando.start(1000)

    def en_juego(self):
        self.ventana_espera.hide()

    def restar_c(self):
        self.ventana_espera.contador -= 1
        if self.ventana_espera.contador < 0:
            self.contando.stop()
            print(' olaaa parando')
            self.ventana_espera.contador = 6
            if self.ventana_espera.comenzar.isEnabled():
                self.inicio_juego_s.emit()
            return
        n = self.ventana_espera.contador
        self.ventana_espera.cuenta_regresiva.setText(f'{n}')


class VentanaEspera(window_name2, base_class2):
    salir_sala_s1 = pyqtSignal()
    inicio_contador_s1 = pyqtSignal()#esta señal la envía el jefe
    inicio_contador_s2 = pyqtSignal()#esta dice qeu debe iniciar el contador
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.salir.clicked.connect(self.salir_sala)
        self.comenzar.clicked.connect(self.inicio_contador_s1.emit)
        self.contador = 6
        self.inicio_contador_s2.connect(self.comenzar_contador)

    def salir_sala(self):
        self.hide()
        self.salir_sala_s1.emit()

    def comenzar_contador(self):
        print(' se inicio el contador exitosamente')

    def comenzar_juego(self):
        pass



class BarraSala(QWidget):
    union_sala_signal = pyqtSignal(dict)
    def __init__(self, parent, nombre, jefe, jugadores, n_jugadores, block):
        super().__init__()
        # self.pushButton.connect(self.boton)
        self.__cant_jug = 0
        self.jefe = jefe
        self.numero = nombre
        self.nombre = QLabel(f'Sala {nombre}',parent)
        self.unirse = QPushButton('Unirse',parent)
        self.n_jugadores = QLabel(f'{n_jugadores}/15', parent)
        self.hvox = QVBoxLayout()
        self.unirse.setEnabled(not(block))


        self.hvox.addWidget(self.nombre)
        self.hvox.addWidget(self.n_jugadores)
        self.hvox.addWidget(self.unirse)
        self.setLayout(self.hvox)
        self.unirse.clicked.connect(self.botonaso)

    def botonaso(self):
        d = {'jefe': self.jefe, 'numero sala': self.numero}
        self.union_sala_signal.emit(d)


    @property
    def cant_jug(self):
        return self.__cant_jug

    @cant_jug.setter
    def cant_jug(self, n):
        self.__cant_jug = n
        self.n_jugadores.setText(f'{n}/15')

    def boton(self):
        pass


class ScrollableSalas(QWidget):
    union_sala = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.vbox = QVBoxLayout()
        self.salas = {}
        self.log_labels = []

    def crear_sala(self, data):
        print('se llama a la funcion')
        self.log_labels = []
        self.deleteLayout(self.layout())
        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignTop)

        if self.layout():
            self.layout().takeAt(0)
        print(data)
        for bar in data:
            print(bar, type(bar))
            lay = BarraSala(self, **bar)
            lay.union_sala_signal.connect(self.boton)
            lay.show()
            self.log_labels.append([lay, bar])
            self.salas['nombre'] = lay
            self.vbox.addWidget(lay)
        self.setLayout(self.vbox)

    def boton(self, data):
        self.union_sala.emit(data)

    def deleteLayout(self, cur_lay):
        ''' Funcion que borra los layouts anteriores
        obtenida de https://gist.github.com/GriMel/181db149cc150d903f1a'''

        if cur_lay is not None:
            while cur_lay.count():
                item = cur_lay.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.deleteLayout(item.layout())
            sip.delete(cur_lay)

    def filtrar_dibujo(self):
        self.send({'status': 'filtro dibujo'})

    def actualizar_botones(self, sala):
        for lab, sala in self.log_labels:
            print(sala)
            lab.unirse.setEnabled(not(sala['block']))


class SubirFoto(QWidget):
    ''' Obtenido de https://pythonspot.com/pyqt5-file-dialog/'''

    def __init__(self, senal):
        super().__init__()
        self.path_obtenido = senal
        self.title = 'PyQt5 file dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.openFileNameDialog()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.path_obtenido.emit(fileName)
            self.close()
