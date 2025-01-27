from rama import Rama
from commit import Commit
from random import randint

class Repositorio:
    def __init__(self):
        self.ramas=[]
        self.index=0
        self.ramas.insert(0, Rama('main', ''))

    def hacer_commit(self, mensaje):
        rama = self.ramas[self.index]
        if rama.commits[0].msj_commit == '':
            rama.commits[0].msj_commit = mensaje
            if len(rama.commits) > 1:
                rama.commits[0].anterior = rama.commits[1].msj_commit
        else:
            self.ramas[self.index].commits.insert(0, Commit(randint(1000, 9999), mensaje, '', self.ramas[self.index].commits[0].msj_commit))

    def crear_rama(self, rama):
        self.ramas.insert(0, Rama(rama, f'Creacion de la rama {rama}'))

    def cambiar_rama(self, rama):
        for i, r in enumerate(self.ramas):
            if r.nombre_rama == rama:
                self.index = i
                return True
        return False

    def merge(self, rama_externa):
        for i, r in enumerate(self.ramas):
            if r.nombre_rama == rama_externa:
                self.ramas[self.index].commits.extend(r.commits) # Esto lo que hace es unir las 2 listas de los commits
                # Si quisiera solo tomar el ultimo commit uso commits.extend(r.commits[0])
                self.ramas[self.index].commits[0].msj_commit = 'Se realizó un merge'
                break

    def mostrar_ramas(self):
        for i, r in enumerate(self.ramas):
            print(f"{r.nombre_rama}")

    def mostrar_historial(self):
        rama = self.ramas[self.index]
        print(f"\nHistorial de la rama {rama.nombre_rama}: ")
        for commit in rama.commits:
            print(f"\t{commit.__str__()}")
        
    