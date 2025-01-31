from commit import Commit
from random import randint

class Rama:
    def __init__(self, nombre_rama, commit_reciente):
        self.nombre_rama = nombre_rama
        self.commit_reciente = commit_reciente # esto es de la clase commit
        self.commits = [] # Lista de commits
        self.archivos = {}
        id = randint(1000, 9999)
        self.commits.insert(0, Commit(id, self.commit_reciente, self.archivos, ''))

    def agregar_archivo(self, archivo):
        self.archivos[archivo.nombre_archivo] = archivo.contenido
        