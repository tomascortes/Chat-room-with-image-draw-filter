__author__ = "jnhasard & pnheinsohn"
'''
Este codigo se sacó de la ayudantía numero 13
del syllabus del 2018
https://github./IIC2233/syllabus-2018-2/tree/master/Ayudantias
'''

import threading as th
import socket
import json
from collections import defaultdict
from funciones_t3 import leer_base_datos, guardar_datos, actualizar
import base64
from filtro import filtro_dibujo
import bcrypt


HOST = 'localhost'
print(HOST)
PORT = 8081

class Servidor:

    def __init__(self):

        self.host = HOST
        self.port = PORT
        self.cant_conexiones = 0
        self.votos_expulsion = defaultdict(set)
        self.contador_salas = 0

        self.socket_servidor = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.bind((self.host, self.port))
        self.socket_servidor.listen(5)
        print(f"Servidor escuchando en {self.host}:{self.port}...")

        thread = th.Thread(target=self.aceptar_conexiones_thread
                            , daemon=True)
        thread.start()
        self.sockets = {}
        self.salas = dict()
        print("Servidor aceptando conexiones...")
        print()

    def aceptar_conexiones_thread(self):
        '''
        Este método es utilizado en el thread para ir aceptando conexiones de
        manera asíncrona al programa principal
        :return:
        '''

        while True:
            client_socket, _ = self.socket_servidor.accept()
            self.sockets[client_socket] = None
            print("Servidor conectado a un nuevo cliente...")

            listening_client_thread = th.Thread(
                target=self.escuchar_cliente_thread,
                args=(client_socket,),
                daemon=True
            )
            listening_client_thread.start()
            if len(self.sockets) > 5:
                break


    def escuchar_cliente_thread(self, client_socket):
        '''
        Este método va a ser usado múltiples veces en threads pero cada vez con
        sockets de clientes distintos.
        :param client_socket: objeto socket correspondiente a algún cliente
        :return:
        '''

        while True:
            try:
                # Primero recibimos los 4 bytes del largo
                response_bytes_length = client_socket.recv(4)
                # Los decodificamos
                response_length = int.from_bytes(response_bytes_length,
                                                 byteorder="big")

                # Luego, creamos un bytearray vacío para juntar el mensaje
                response = bytearray()

                # Recibimos datos hasta que alcancemos la totalidad de los datos
                # indicados en los primeros 4 bytes recibidos.
                while len(response) < response_length:
                    bytes_leer = min(256, response_length - len(response))
                    response += client_socket.recv(bytes_leer)

                # Una vez que tenemos todos los bytes, entonces ahí decodificamos
                response = response.decode()

                decoded = json.loads(response)

                # Luego, debemos cargar lo anterior utilxizando json

                # Para evitar hacer muy largo este método, el manejo del mensaje se
                # realizará en otro método
                self.manejar_comando(decoded, client_socket)

            except ConnectionResetError:
                decoded_message = {"status": "cerrar_sesion"}
                self.manejar_comando(decoded_message, client_socket)
                break

    def manejar_comando(self, recibido, client_socket):
        '''
        Este método toma lo recibido por el cliente correspondiente al socket pasado
        como argumento.
        :param recibido: diccionario de la forma: {"status": tipo, "data": información}
        :param client_socket: socket correspondiente al cliente que envió el mensaje
        :return:
        '''

        # Podemos imprimir para verificar que toodo anda bien

        if recibido["status"] == "mensaje":
            #inlcuimos sala
            nombre = self.sockets[client_socket]['nombre']
            for skt, sala in self.salas.items():
                if nombre in sala['jugadores']:
                    jugadores = sala['jugadores']
                    sala = sala['nombre']
                    break
            msj = {"status": "mensaje",
                   "data": {"usuario": self.sockets[client_socket]['nombre'],
                            "contenido": recibido["data"]["contenido"],
                            'sala': sala}}
            borrar = 0

            #aqui vemos si es un comando lo que llega
            voto_elim = self.comando_valido(recibido["data"]["contenido"])
            if voto_elim:
                self.votos_expulsion[voto_elim].add(msj['data']['usuario'])

            else:
                for skt, usr in self.sockets.items():
                    if usr['nombre'] in jugadores:
                        self.send(msj, skt)

            if len(recibido["data"]["contenido"]) > 1 and voto_elim:
                if len(self.votos_expulsion[voto_elim]) > len(jugadores)//2:
                    print(f'expulsado el usuario {voto_elim}')
                    for skt, usr in self.sockets.items():
                        if usr['nombre'] in jugadores:
                            msj2 = {"status": "eliminacion",
                               "data":f'{voto_elim}'}
                            self.send(msj2, skt)
                            borrar = 1

            if borrar != 0:
                #hacer esto despues
                pass

        elif recibido["status"] == "nuevo_usuario":
            base = leer_base_datos()
            nombre = recibido['data']['nombre']
            contrasena = recibido['data']['contrasena']
            contrasena = contrasena.encode('utf-8')
            hashed = bcrypt.hashpw(contrasena, bcrypt.gensalt(14))

            for usr in self.sockets.values():
                if usr != None:
                    if (nombre == usr['nombre']
                    or nombre == 'empty'):
                        print('usuario ya registrado ')
                        self.send({'status':'usr en linea'}, client_socket)
                        return

            for n, usr in enumerate(base, 0):
                if usr != None:
                    if( usr['nombre'] == nombre
                    and self.contraena_corresp(
                        contrasena, usr['contrasena'])):

                        self.sockets[client_socket] = usr
                        self.send({'status':'usr aceptado'}, client_socket)
                        self.send_img(client_socket, usr['foto'])
                        self.send(
                                {'status': 'act sala',
                                'data': [v for v in self.salas.values()]}
                                , client_socket)
                        return
                    elif (usr['nombre'] == nombre):
                        self.send({'status': 'contrasena mala'}
                                    , client_socket)
                        return

            hashed = hashed.decode('utf-8')

            new = {"nombre": recibido["data"]['nombre']
            , "foto": "empty.png", "id": 0
            ,"contrasena": hashed}
            self.sockets[client_socket] = new
            base.append(new)
            self.send({'status':'usr aceptado'}, client_socket)
            guardar_datos(base)
            self.send_img(client_socket, "empty.png")
            self.send(
                    {'status': 'act sala',
                    'data': [v for v in self.salas.values()]}, client_socket)

        elif recibido['status'] == 'cambio usuario':
            self.abandono_sala(client_socket)
            self.act_salas()

        elif recibido['status'] == 'new_img':
            response_bytes_length = client_socket.recv(4)
            response_length = int.from_bytes(response_bytes_length,
                                             byteorder="big")
            response = bytearray()
            while len(response) < response_length:
                bytes_leer = min(256, response_length - len(response))
                response += client_socket.recv(bytes_leer)

            path = self.sockets[client_socket]['nombre']
            with open(f'imagenes/{path}.png', 'wb') as f:
                f.write(response)
            print(path)
            self.sockets[client_socket]['foto'] = f'{path}.png'
            actualizar(self.sockets[client_socket])
            self.send_img(client_socket, path + '.png')


        elif recibido['status'] == 'crear sala':
            #el numero de salas nunca se reiniciará
            if not(client_socket in self.salas.keys()):
                jefe = self.sockets[client_socket]['nombre']
                self.contador_salas += 1
                nombre = f'Sala numero {self.contador_salas}'
                self.salas[client_socket] = {'jefe': jefe,
                        'nombre': self.contador_salas,'jugadores': [jefe],
                        'n_jugadores': 1, 'block': False}
                self.act_salas()
                d = {'status': 'aceptado sala'
                        , 'data': {'jefe': jefe
                                    , 'n_sala': self.contador_salas
                                    , 'sala': self.salas[client_socket]}}
                self.send(d, client_socket)

        elif recibido['status'] == 'union sala':
            jefe = recibido['data']['jefe']
            nombre = self.sockets[client_socket]['nombre']
            for skt, val in self.sockets.items():
                if (val['nombre'] == jefe
                and (nombre not in self.salas[skt]['jugadores'])):
                    if self.salas[skt]['n_jugadores'] < 15 - 1:
                        self.salas[skt]['jugadores'].append(nombre)
                        self.salas[skt]['n_jugadores'] += 1
                        sala = self.salas[skt]

                    elif self.salas[skt]['n_jugadores'] == 15 - 1:
                        self.salas[skt]['jugadores'].append(nombre)
                        self.salas[skt]['n_jugadores'] += 1
                        self.salas[skt]['block'] = True
                        sala = self.salas[skt]

                    elif self.salas[skt]['n_jugadores'] >= 15:
                        print('esto es imposible')
                        return

            self.act_salas()
            self.send({'status': 'aceptado sala'
                        , 'data': {'jefe': jefe
                                    , 'n_sala': sala['nombre']
                                    , 'sala': sala}},
                        client_socket)

        elif recibido['status'] == 'salir sala':
            self.abandono_sala(client_socket)
            self.act_salas()

        elif recibido['status'] == 'inicio contador':
            jug = self.salas[client_socket]['jugadores']
            for skt, usr in self.sockets.items():
                if usr['nombre'] in jug:
                    msj = {'status': 'inicio contador'}
                    self.send(msj, skt)

        elif recibido['status'] == 'inicio juego':
            if client_socket not in self.salas:
                return
            jug = self.salas[client_socket]['jugadores']
            sala =  self.salas[client_socket]
            self.salas[client_socket]['block'] = True
            for skt, usr in self.sockets.items():
                if usr['nombre'] in jug:
                    msj = {'status': 'inicio juego', 'sala': sala}
                    self.send(msj, skt)
            self.act_salas()

        elif recibido['status'] == 'filtro dibujo':
            path = self.sockets[client_socket]['foto']
            nd = filtro_dibujo('imagenes/' + path)
            with open('imagenes/' + path, 'wb') as f:
                f.write(nd)
            self.send_img(client_socket, path)

        elif recibido["status"] == "cerrar_sesion":
            name = self.sockets[client_socket]['nombre']
            print(name, ' ha abandonado')
            for i in self.votos_expulsion:
                if name in self.votos_expulsion[i]:
                    self.votos_expulsion[i].remove(name)

            self.abandono_sala(client_socket)
            del self.sockets[client_socket]
            self.act_salas()

    def send_img(self, skt, path):
        with open('imagenes/' + path , 'rb') as f:
            data = f.read()

        #enviamos el aviso de que se enviará una foto
        self.send({'status': 'img_usr'}, skt)
        msg_length = len(data).to_bytes(4, byteorder="big")
        # Finalmente, los enviamos al servidor
        skt.send(msg_length + data)

    def abandono_sala(self, jskt):
        if jskt in self.salas:
            print('cambio de jefe')
            jefe = self.sockets[jskt]['nombre']
            sala = self.salas[jskt]
            sala['jugadores'].remove(jefe)
            sala['n_jugadores'] -= 1
            otros_j = sala['jugadores']
            del self.salas[jskt]
            if len(otros_j) > 0:
                n_j = otros_j[0]
                for skt, datos in self.sockets.items():
                    if datos['nombre'] == n_j:
                        sala['jefe'] = n_j
                        self.salas[skt] = sala

        else:
            nombre = self.sockets[jskt]['nombre']
            for skt, sala in  self.salas.items():
                if nombre in  self.salas[skt]['jugadores']:
                    self.salas[skt]['jugadores'].remove(nombre)
                    self.salas[skt]['n_jugadores'] -= 1

    def act_salas(self):
        for skt in self.sockets:
            self.send(
                {'status': 'act sala',
                 'data': [v for v in self.salas.values()]}, skt)

    def comando_valido(self, msj):
        for skt in self.sockets.keys():
            posible_com = msj.split(' ')
            if posible_com[0] == '\\chao':
                if len(posible_com) > 1:
                    for usr in self.sockets.values():
                        if posible_com[1] == usr['nombre']:
                            return posible_com[1]

            return False

    def contraena_corresp(self, contrasena, guardada):
        ''' obtenido de https://pypi.org/project/bcrypt/'''
        guardada = guardada.encode('utf-8')
        if bcrypt.checkpw(contrasena, guardada):
            return True
        else:
            return False

    @staticmethod
    def send(valor, socket):
        '''
        Este método envía la información al cliente correspondiente al socket.
        :param msg: diccionario del tipo {"status": tipo del mensaje, "data": información}
        :param socket: socket del cliente al cual se le enviará el mensaje
        :return:
        '''
        # Le hacemos json.dumps y luego lo transformamos a bytes
        msg_json = json.dumps(valor)
        msg_bytes = msg_json.encode()

        # Luego tomamos el largo de los bytes y creamos 4 bytes de esto
        msg_length = len(msg_bytes).to_bytes(4, byteorder="big")

        # Finalmente, los enviamos al servidor
        socket.send(msg_length + msg_bytes)
