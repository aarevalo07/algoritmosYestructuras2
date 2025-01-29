class Jugador:
    """
    def __init__(self, nombre, tipo, vida, ataque, defensa, alcance): # Tipo es un objeto de la clase unidad
        self.nombre = nombre
        self.tipo = tipo
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa
        self.alcance = alcance
    """
    def __init__(self, nombre, vida,unidades=[]):
        self.nombre = nombre
        self.vida = vida
        self.unidades = unidades
    
    def agregar_unidades(self, unidad):
        self.unidades.append(unidad)

class Unidad:
    def __init__(self, nombre, vida, ataque, defensa, alcance, coordenadas=[]):
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa
        self.alcance = alcance
        self.coordenadas = coordenadas
    
    def actualizar_coord(self, coordenadas):
        self.coordenadas = coordenadas
    
    def atacar(self, objetivo):
        objetivo.vida -= self.ataque - objetivo.defensa

class Guerrero(Unidad):
    def __init__(self, nombre, vida, ataque, defensa, alcance, coordenadas, habilidades=[]):
        super().__init__(nombre, vida, ataque, defensa, alcance, coordenadas)
        self.habilidadGuerrero = habilidades

    def aplicar_habilidad(self, nombreHabilidad):
        pass