from commit import Commit
from random import randint

class Rama:
    def __init__(self, nombre_rama, recent):
        self.nombre_rama = nombre_rama
        self.recent = recent # esto es de la clase commit
        self.commits = [] # Lista de commits
        id = randint(1000, 9999)
        if len(self.commits) == 0:
            self.commits.insert(0, Commit(id, self.recent, '', ''))
        else:
            while Commit.id == id:
                id = randint(1000, 9999)
            self.commits.insert(0, Commit(id, self.recent, '', self.commits[1].msj_commit))
        