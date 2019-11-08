from pixel_collector import *
import zlib
import math

def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def matriz_a_png(img):
    #HEADER
    png =  [137, 80, 78, 71, 13, 10, 26, 10]
    header = bytearray()
    for i in png:
        header += i.to_bytes(1, byteorder="big")

    #CHUNK
    tipo = 'IHDR'.encode('ASCII')

    ancho = len(img[0]).to_bytes(4, byteorder="big")
    alto = len(img).to_bytes(4, byteorder="big")
    metadata = bytearray()

    for i in [8 ,2,0,0,0]:
        metadata += i.to_bytes(1, byteorder="big")

    informacion = ancho + alto + metadata
    crc = zlib.crc32(tipo + informacion)
    crc = int_to_bytes(crc)
    largo_info = (13).to_bytes(4, byteorder="big")
    chunk = largo_info + tipo + informacion + crc

    #idat
    l = []
    #for i in range(len(img)):
    #    l.append([(0).to_bytes(1, byteorder="big")])

    for n,fila in enumerate(img):
        aux = [(0).to_bytes(1, byteorder="big")]
        for elem in fila:
            rgb = [x.to_bytes(1, byteorder="big") for x in elem]
            aux.extend(rgb)
            #aux += b''.join(rgb)

        l.append(b''.join(aux))

    l = b''.join(l)

    tipo2 = 'IDAT'.encode('ASCII')
    comp = zlib.compress(l)
    crc2 = zlib.crc32(tipo2 + comp)
    crc2 = int_to_bytes(crc2)
    largo2 = len(comp).to_bytes(4, byteorder="big")



    idat = largo2 + tipo2  + comp + crc2
    #iend

    tipo3 = 'IEND'.encode('ASCII')
    crc3 = zlib.crc32(tipo3)
    crc3 = int_to_bytes(crc3)
    largo3 = (0).to_bytes(4, byteorder='big')
    ident = largo3 + tipo3 + crc3

    final = header + chunk + idat + ident
    return final

def escala_grises(mat):
    m2 = []
    for fila in mat:
        matriz_aux = []
        for val in fila:
            r, g, b = val
            v = r * 0.299 + g * 0.587 + b * 0.144
            v = int(v)
            matriz_aux.append([v, v, v])
        m2.append(matriz_aux)
    return m2

def convolucion(matr, nucleo):
    m = len(matr[0])
    n = len(matr)
    x = len(nucleo[0])
    y = len(nucleo)

    filas = m - x + 1
    columnas = n - y + 1

    conv = []
    for alto in range(filas):
        aux = []
        for ancho in range(columnas):
            suma = 0
            for a in range(x):
                for b in range(y):
                    v = matr[a + ancho][b + alto][0] * nucleo[a][b]
                    suma += v
            aux.append([suma, suma, suma])
        conv.append(aux)
    return conv

def gradiente(matr, c1,c2):
    d = []
    for fil in range(len(c1[0])):
        aux = []
        for col in range(len(c1)):
            v = c1[col][fil][0]**2 + c2[col][fil][0]**2
            v = math.sqrt(v)
            aux.append([v, v, v])
        d.append(aux)

    return d

def binarizar(mat, cota):
    m2 = []
    for fila in mat:
        matriz_aux = []
        for val in fila:
            rgb = []

            for color in val:
                if color < cota:
                    color = 0
                else:
                    color = 255
                rgb.append(color)
            matriz_aux.append(rgb)
        m2.append(matriz_aux)
    return m2

def inversion_colores(mat):
    m2 = []
    for fila in mat:
        matriz_aux = []
        for val in fila:
            rgb = []
            for color in val:
                if color:
                    color = 0
                else:
                    color = 255
                rgb.append(color)
            matriz_aux.append(rgb)
        m2.append(matriz_aux)
    return m2



def filtro_dibujo(path):
    img = get_pixels(path)

    img = escala_grises(img)

    nuc_1 = [[1, 0], [0, -1]]
    nuc_2 = [[0, 1], [-1, 0]]



    conv1 = convolucion(img, nuc_1)

    conv2 = convolucion(img, nuc_2)

    img = gradiente(img, conv1, conv2)

    img = binarizar(img, 30)

    img = inversion_colores(img)

    final = matriz_a_png(img)
    return final
