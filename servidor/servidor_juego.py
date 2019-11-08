
import threading as th
import socket
import json
from collections import defaultdict
from funciones_t3 import leer_base_datos, guardar_datos, actualizar
import base64
from filtro import filtro_dibujo
from parametros import N,M

class ServidorJuego:
    def __init__(self):
        self.matriz = []
        for i in range(N):
            self.matriz.append([])
            for j in range(M):
                self.matriz[i].append([False])
