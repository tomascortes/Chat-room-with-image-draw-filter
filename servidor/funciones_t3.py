import json
def leer_base_datos():
    path = 'base_datos.txt'
    l = []
    with open(path, 'r', encoding = 'utf-8') as f:
        for linea in f:
            l.append(json.loads(linea))
    return l

def guardar_datos(datos):
    path = 'base_datos.txt'
    with open(path, 'w') as f:
        for i in datos:
            f.write(json.dumps(i) + '\n')

def actualizar(usuario_act):
    base = leer_base_datos()
    for n, usr in enumerate(base):
        if usuario_act['nombre'] == usr['nombre']:
            print(usr)
            base[n]['foto'] = usuario_act['foto']
    guardar_datos(base)
