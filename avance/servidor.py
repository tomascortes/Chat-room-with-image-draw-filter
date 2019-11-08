__author__ = "jnhasard & pnheinsohn"
'''
Este codigo se sacó de la ayudantía numero 13
del syllabus del 2018
https://github.com/IIC2233/syllabus-2018-2/tree/master/Ayudantias
'''




import threading as th
import socket
import json
from collections import defaultdict

HOST = socket.gethostname()
PORT = 8081

class Servidor:

    def __init__(self):

        self.host = HOST
        self.port = PORT
        self.cant_conexiones = 0
        self.votos_expulsion = defaultdict(set)

        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.bind((self.host, self.port))
        self.socket_servidor.listen(5)
        print(f"Servidor escuchando en {self.host}:{self.port}...")

        thread = th.Thread(target=self.aceptar_conexiones_thread, daemon=True)
        thread.start()
        self.sockets = {}
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
            self.cant_conexiones += 1

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
                    response += client_socket.recv(256)

                # Una vez que tenemos todos los bytes, entonces ahí decodificamos
                response = response.decode()

                # Luego, debemos cargar lo anterior utilxizando json
                print(type(response), ' pre error')
                decoded = json.loads(response)
                print('post error')
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
            msj = {"status": "mensaje",
                   "data": {"usuario": self.sockets[client_socket],
                            "contenido": recibido["data"]["contenido"]}}
            borrar = 0
            for skt in self.sockets.keys():
                posible_com = recibido["data"]["contenido"].split(' ')
                if posible_com[0] == '\\chao':
                    if len(posible_com) > 1:
                        if posible_com[1] in self.sockets.values():
                            self.votos_expulsion[posible_com[1]].add(msj['data']['usuario'])
                else:
                    self.send(msj, skt)

                if len(posible_com) > 1:
                    if len(self.votos_expulsion[posible_com[1]]) > len(self.sockets)//2:
                        print(f'expulsado el usuario {posible_com[1]}')
                        for skt in self.sockets.keys():
                            msj = {"status": "eliminacion",
                                   "data":f'{posible_com[1]}'}
                            self.send(msj, skt)

            if borrar != 0:
                del self.sockets[posible_com[1]]

        elif recibido["status"] == "nuevo_usuario":
            self.sockets[client_socket] = recibido["data"]

        elif recibido["status"] == "cerrar_sesion":
            name = self.sockets[client_socket]
            for i in self.votos_expulsion:
                if name in self.votos_expulsion[i]:
                    self.votos_expulsion[i].remove(name)
            del self.sockets[client_socket]



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

if __name__ == "__main__":


    server = Servidor()

    # Mantenemos al server corriendo
    while True:
        pass
