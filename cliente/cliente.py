__author__ = "jnhasard & pnheinsohn"
'''
Este codigo se sacó de la ayudantía numero 13
del syllabus del 2018
https://github.com/IIC2233/syllabus-2018-2/tree/master/Ayudantias
'''

import sys
import threading as th
import socket
import json
from frontmenu import VentanaPrincipal
from frontchat import  VentanaChat
from PyQt5.QtWidgets import QApplication
from datetime import datetime
from sala_seleccion import Seleccion
import base64
import time
from frontjuego import Juego

HOST = 'localhost'
PORT = 8081

class Cliente:
    '''
    Esta es la clase encargada de conectarse con
    el servidor e intercambiar información
    '''

    def __init__(self):
        print("Inicializando cliente...")
        self.socket_cliente = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)

        self.host = HOST
        self.port = PORT
        self.envio = th.Lock()
        self.jefe = bool()
        self.nombre_usr = ''
        self.n_sala = None
        self.en_juego = False

        #ventana principal
        self.frontend = VentanaPrincipal(self)
        self.frontend.servidor_signal.connect(self.pos_nombre)
        self.frontend.terminar_conexion_signal.connect(
                                            self.terminar_conexion)
        self.frontend.cerrar_v_principal.connect(self.frontend.hide)
        self.frontend.fallo_usr.connect(self.frontend.usr_enlinea)

        #menu de selección de salas
        self.front_selec = Seleccion()
        self.front_selec.path_obtenido.connect(self.subir_img)
        self.front_selec.senal_sala.connect(self.crear_sala)
        self.front_selec.cerrar_sesion.clicked.connect(self.cambio_usr)

        self.front_selec.scrollable.union_sala.connect(self.solicitud_union)

        self.front_selec.salir_sala_s2.connect(self.salir_sala_b)
        self.front_selec.ventana_espera.inicio_contador_s1.connect(
                                                self.aviso_contador)
        self.front_selec.inicio_juego_s.connect(self.inicio_juego)
        self.front_selec.filtro_dibujo.clicked.connect(self.filtro_dibujo)

        #ventana de juego
        self.ventana_chat = VentanaChat(self.frontend.servidor_signal,
            self.frontend.terminar_conexion_signal)
        self.ventana_chat.start_s.connect(self.ventana_chat.start)

        self.frontend.nombre_usuario.connect(self.ventana_chat.nombre)
        self.frontend.show()

        self.front_juego = Juego()


        try:
            self.socket_cliente.connect((self.host, self.port))
            print("Cliente conectado exitosamente al servidor")

            self.conectado = True

            escuchar_servidor = th.Thread(target=self.escuchar, daemon=True)
            escuchar_servidor.start()
            print("Escuchando al servidor...")

        except ConnectionRefusedError:
            self.terminar_conexion()

    def escuchar(self):
        '''
        Este método es usado en el thread y la idea es que reciba lo que
        envía el servidor. Implementa el protocolo de agregar los primeros
        4 bytes, que indican el largo del mensaje
        '''
        while self.conectado:
            try:
                # Recibimos los 4 bytes del largo
                tamano_mensaje_bytes = self.socket_cliente.recv(4)
                tamano_mensaje = int.from_bytes(
                                tamano_mensaje_bytes, byteorder="big")
                cont = bytearray()
                # Recibimos el resto de los datos
                while len(cont) < tamano_mensaje:
                    bytes_leer = min(256, tamano_mensaje - len(cont))
                    cont += self.socket_cliente.recv(bytes_leer)

                # Decodificamos y pasamos a JSON el mensaje
                cont = cont.decode("utf-8")
                mensaje_decodificado = json.loads(cont)

                # Manejamos el mensaje
                self.manejar_comando(mensaje_decodificado)

            except ConnectionResetError:
                self.servidor_caido()

    def manejar_comando(self, diccionario):
        '''
        Este método toma el mensaje decodificado de la forma:
        {"status": tipo del mensaje, "data": información}
        '''
        if diccionario["status"] == "mensaje":
            data = diccionario["data"]
            usuario = data["usuario"]
            contenido = data["contenido"]
            sala = data['sala']
            if self.n_sala == sala:
                usuario = "({}:{}) {}".format(datetime.now().hour,
                                            datetime.now().minute,
                                            usuario)
                self.ventana_chat.actualizar_chat(f"{usuario}: {contenido}")


        elif diccionario["status"] == "eliminacion":
            print('alguien fue eliminado')
            if diccionario["data"] == self.ventana_chat.nombre_usuario:
                if self.en_juego:
                    pass#sacarlo de otra format
                    return
                self.front_selec.ventana_espera.salir.clicked.emit()

            else:
                data = diccionario["data"]
                usuario = 'servidor'
                contenido = f'El integrante {data} fue eliminado por voto popular'
                usuario = f"({datetime.now().hour}:{datetime.now().minute}) {usuario}"
                self.ventana_chat.actualizar_chat(f"{usuario}: {contenido}")

        elif diccionario["status"] == "usr en linea":
            print('este usuario ya está en linea')
            self.frontend.fallo_usr.emit()

        elif diccionario["status"] == "usr aceptado":
            print('aceptado')
            self.frontend.cerrar_v_principal.emit()
            self.front_selec.mostrar_sala_selec.emit()

        elif diccionario['status'] == 'contrasena mala':
            self.frontend.contrasena_incorrecta()

        elif diccionario['status'] == 'img_usr':
            data = bytearray()
            tamano_mensaje_bytes = self.socket_cliente.recv(4)
            tamano_mensaje = int.from_bytes(tamano_mensaje_bytes, byteorder="big")
            # Recibimos el resto de los datos

            while len(data) < tamano_mensaje:
                bytes_leer = min(256, tamano_mensaje - len(data))
                data += self.socket_cliente.recv(bytes_leer)

            self.front_selec.cargar_px.emit(data)

        elif diccionario['status'] == 'act sala':
            salas = diccionario['data']
            self.front_selec.sala_aceptada.emit(salas)
            jug = ''
            ptje = 0
            for sala in salas:
                if self.nombre_usr in sala['jugadores']:
                    for i in sala['jugadores']:
                        jug += f'{i} : {ptje}\n'
                    self.ventana_chat.actualizar_lista_jug(jug)
                    self.front_selec.scrollable.actualizar_botones(sala)
                    if self.nombre_usr == sala['jefe']:
                        self.front_selec.ventana_espera.comenzar.show()
                        self.front_selec.ventana_espera.comenzar.setEnabled(
                                                            True)

        elif diccionario['status'] == 'union sala':
            self.n_sala = diccionario['data']

        elif diccionario['status'] == 'aceptado sala':
            self.n_sala = diccionario['data']['n_sala']
            sala = diccionario['data']['sala']
            jefe = diccionario['data']['jefe']

            self.front_selec.sala_espera.emit(jefe)
            self.ventana_chat.start_s.emit()
            if jefe != self.nombre_usr:
                self.front_selec.ventana_espera.comenzar.hide()
                self.front_selec.ventana_espera.comenzar.setEnabled(False)
            else:
                self.front_selec.ventana_espera.comenzar.show()
                self.front_selec.ventana_espera.comenzar.setEnabled(True)

            jug = 'Lista Jugadores en linea \n'
            ptje = 0
            for i in sala['jugadores']:
                jug += f'{i} : {ptje}\n'
            self.ventana_chat.actualizar_lista_jug(jug)
            self.front_selec.scrollable.actualizar_botones(sala)


        elif diccionario['status'] == 'inicio contador':
            self.front_selec.ventana_espera.inicio_contador_s2.emit()

        elif diccionario['status'] == 'inicio juego':
            self.front_selec.en_juego_s.emit()
            self.front_juego.inicio.emit()
            self.front_juego.nombre = self.nombre_usr
            self.en_juego = True
            sala = diccionario['sala']
            self.front_selec.scrollable.actualizar_botones(sala)


    def send(self, mensaje):
        '''
        Este método envía la información al servidor. Recibe un mensaje del tipo:
        {"status": tipo del mensaje, "data": información}
        '''

        with self.envio:
            print('estamos mandando ', mensaje)

            # Codificamos y pasamos a bytes
            mensaje_codificado = json.dumps(mensaje)
            contenido_mensaje_bytes = mensaje_codificado.encode("utf-8")

            # Tomamos el largo del mensaje y creamos 4 bytes de esto
            tamano_mensaje_bytes = len(
                    contenido_mensaje_bytes).to_bytes(4, byteorder="big")

            # Enviamos al servidor
            self.socket_cliente.send(
                    tamano_mensaje_bytes + contenido_mensaje_bytes)

    def subir_img(self, path):
        with open(path, 'rb') as f:
            data = f.read()
        msj = {'status':'new_img'}
        self.send(msj)

        contenido_mensaje_bytes = data
        tamano_mensaje_bytes = len(
                contenido_mensaje_bytes).to_bytes(4, byteorder="big")
        with self.envio:
            self.socket_cliente.send(
                    tamano_mensaje_bytes + contenido_mensaje_bytes)

    def pos_nombre(self, msj):
        self.nombre_usr = msj['data']['nombre']
        self.send(msj)

    def terminar_conexion(self):
        print("Conexión terminada")
        t = 'Estamos haciendole mantención a nuestros '
        t += 'servidores muchas gracias por su comprensión'
        print(t)
        self.conectado = False
        self.frontend.hide()
        self.front_juego.hide()
        self.front_selec.hide()
        self.ventana_chat.hide()
        self.socket_cliente.close()
        exit()

    def crear_sala(self):
        self.send({'status':'crear sala'})

    def solicitud_union(self, data):
        if data['jefe'] == self.nombre_usr:
            return
        msj = {'status': 'union sala','data': data}
        self.send(msj)

    def salir_sala_b(self):
        self.ventana_chat.esconder.emit()
        self.send({'status': 'salir sala', 'data': self.n_sala})

    def aviso_contador(self):
        self.send({'status': 'inicio contador'})

    def inicio_juego(self):
        self.send({'status': 'inicio juego'})

    def filtro_dibujo(self):
        self.send({'status': 'filtro dibujo'})

    def cambio_usr(self):
        self.frontend.show()
        self.front_selec.hide()
        self.send({'status': 'cambio usuario'})

    def servidor_caido(self):
        # self.frontend.server_caido.emit()
        print('se cayó el servidor')
        self.terminar_conexion()
