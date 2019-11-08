class Persona(json.JSONEncoder):
    '''
    Clase obtenida de los contenidos, en la que se almacena la
    información de cada persona
    '''
    id = count()

    def __init__(self, nombre = nombre, foto = foto):
        self.nombre = nombre
        self.foto = foto
        self.id_ = next(self.id)
        self.logged = 1
        # Mantenemos la serialización por defecto para otros tipos
        return super().default(obj)
