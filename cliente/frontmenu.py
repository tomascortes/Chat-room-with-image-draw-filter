from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout,\
 QVBoxLayout, QMessageBox
from PyQt5.QtWidgets import QPushButton, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor


'''
Este codigo se sacó de la ayudantía numero 13
del syllabus del 2018
https://github.com/IIC2233/syllabus-2018-2/tree/master/Ayudantias
'''

class VentanaPrincipal(QWidget):
    servidor_signal = pyqtSignal(dict)
    terminar_conexion_signal = pyqtSignal()
    cerrar_v_principal = pyqtSignal()
    fallo_usr = pyqtSignal()
    nombre_usuario = pyqtSignal(str)
    fallo_pass = pyqtSignal()
    server_caido = pyqtSignal()



    def __init__(self, cliente, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # señales
        self.fallo_usr.connect(self.usr_enlinea)
        self.fallo_pass.connect(self.contrasena_incorrecta)
        self.server_caido.connect(self.server_c)




        # Instancias de UI
        self.setWindowTitle("Timbiriche")
        self.setGeometry(400, 200, 640, 480)

        self.label_titulo = QLabel("Timbiriche", self)
        label_titulo_font = self.label_titulo.font()
        label_titulo_font.setBold(True)
        label_titulo_font.setPointSize(28)
        self.label_titulo.setFont(label_titulo_font)
        self.label_titulo.setStyleSheet("color: darkblue")

        self.label_usuario = QLabel("Username: ", self)
        label_usuario_font = self.label_usuario.font()
        label_usuario_font.setBold(True)
        label_usuario_font.setPointSize(12)
        self.label_usuario.setFont(label_usuario_font)
        self.label_usuario.setStyleSheet("color: darkblue")

        self.label_password = QLabel("Contrasena: ", self)
        label_password_font = self.label_password.font()
        label_password_font.setBold(True)
        label_password_font.setPointSize(12)
        self.label_password.setFont(label_password_font)
        self.label_password.setStyleSheet("color: darkblue")

        self.usuario_line_edit = QLineEdit("", self)
        usuario_line_edit_font = self.usuario_line_edit.font()
        usuario_line_edit_font.setPointSize(10)
        self.usuario_line_edit.setFont(usuario_line_edit_font)
        colors = "color: darkblue; background: transparent"
        self.usuario_line_edit.setStyleSheet(colors)

        self.password_line_edit = QLineEdit("", self)
        password_line_edit_font = self.password_line_edit.font()
        password_line_edit_font.setPointSize(10)
        self.password_line_edit.setFont(password_line_edit_font)
        self.password_line_edit.setStyleSheet(colors)

        self.boton_usuario = QPushButton("\t\tIngresar\t\t", self)
        boton_usuario_font = self.boton_usuario.font()
        boton_usuario_font.setBold(False)
        boton_usuario_font.setPointSize(12)
        self.boton_usuario.setFont(boton_usuario_font)
        self.boton_usuario.setStyleSheet(
            "QPushButton{color: darkblue; background: transparent; border: 2px solid darkblue; border-radius: 8px}"
            "QPushButton:pressed{color: #fcf7e3; background-color: darkblue}")
        self.boton_usuario.clicked.connect(self.manejo_boton)

        self.error = QLabel("", self)


        # Alineación de UI
        self.init_setUp()

    def init_setUp(self):
        hbox = QHBoxLayout()
        hbox.addStretch(2)
        hbox.addWidget(self.label_usuario)
        hbox.addWidget(self.usuario_line_edit)
        hbox.addWidget(self.error)
        hbox.addStretch(2)

        hbox1 = QHBoxLayout()
        hbox1.addStretch(2)
        hbox1.addWidget(self.label_password)
        hbox1.addWidget(self.password_line_edit)
        hbox1.addStretch(2)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(2)
        hbox2.addWidget(self.boton_usuario)
        hbox2.addStretch(2)

        title_hbox = QHBoxLayout()
        title_hbox.addStretch(1)
        title_hbox.addWidget(self.label_titulo)
        title_hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(title_hbox)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        # vbox.addLayout(hbox3)
        vbox.addStretch(3)

        self.setLayout(vbox)

    def manejo_boton(self):
        if len(self.usuario_line_edit.text()) != 0:
            nombre = self.usuario_line_edit.text()
            contrasena = self.password_line_edit.text()
            if len(contrasena) < 6:
                self.error.setText('contrasena muy corta')
                return

            self.nombre_usuario.emit(nombre)
            mensaje = {"status": "nuevo_usuario"
                    , "data": {'nombre': nombre,'contrasena': contrasena}}
            self.servidor_signal.emit(mensaje)

    def cerrar(self):
        self.close()

    def usr_enlinea(self):
        self.error.setText('este usario ya se encuentra jugando')

    def contrasena_incorrecta(self):
        self.error.setText('Contrasena incorrecta')

    def server_c(self):
        buttonReply = QMessageBox.question(self
            , 'PyQt5 message', "Do you like PyQt5?"
            , QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            print('Yes clicked.')
        else:
            print('No clicked.')
