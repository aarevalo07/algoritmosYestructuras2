from rama import Rama
from commit import Commit
from archivo import Archivo
from random import randint

class Repositorio:
    def __init__(self):
        self.ramas=[] # Contiene una lista de los objetos de la clase Rama
        self.index=0 # Contador para la ubicacion de la rama actual
        self.ramas.insert(0, Rama('main', 'Commit inicial')) # Al iniciar el repositorio se crea por defecto la rama main

    # Metodo que crea la clase Archivo y la guarda en un objeto de la clase Rama
    def agregar_archivo(self, nombre_archivo, contenido):
        self.ramas[self.index].agregar_archivo(Archivo(nombre_archivo, contenido)) # agregar_archivo: metodo de la clase rama

    # Crea el objeto de la clase commit que se almacena en commits=[], objeto de la clase Rama
    def hacer_commit(self, mensaje):
        rama = self.ramas[self.index]
        if len(rama.commits) > 1: # Condicional para almacenar el commit anterior
            rama.commits[0].anterior = rama.commits[1].msj_commit
        rama.commits.insert(0, Commit(randint(1000, 9999), mensaje, rama.archivos, rama.commits[0].msj_commit))

    # Crea el objeto de la clase rama con su mensaje commit
    def crear_rama(self, rama):
        self.ramas.insert(0, Rama(rama, f'Creacion de la rama {rama}'))

    # Realiza un git checkout a la rama de eleccion, solo cambia el valor del index para ubicar la rama, sino, la rama no existe
    def cambiar_rama(self, rama):
        for i, r in enumerate(self.ramas):
            if r.nombre_rama == rama:
                self.index = i
                return True
        return False

    # git merge
    def merge(self, rama_externa):
        for i, r in enumerate(self.ramas):
            if r.nombre_rama == rama_externa:
                self.ramas[self.index].commits.extend(r.commits) # Esto lo que hace es unir las 2 listas de los commits
                # Si quisiera solo tomar el ultimo commit uso commits.extend(r.commits[0])
                self.ramas[self.index].commits[0].msj_commit = 'Se realizó un merge'
                break

    # Muestra las ramas disponibles
    def mostrar_ramas(self):
        for i, r in enumerate(self.ramas):
            print(f"{r.nombre_rama}")

    # Realiza un git log de su preferencia
    def mostrar_historial(self):
        rama = self.ramas[self.index]
        print(f"\nHistorial de la rama {rama.nombre_rama}: ")
        # Si quiere hacer un git log de todos los commits, descomente esto
        # for commit in rama.commits:
        #     print(f"\t{commit.__str__()}")
        print(f"\t{rama.commits[0].__str__()}")
        
    