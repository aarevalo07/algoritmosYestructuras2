import datetime
import getpass

class Commit:
    def __init__(self, id, msj_commit, archivos=None, anterior=None):
        self.id = id
        self.msj_commit = msj_commit
        self.author = getpass.getuser()
        self.date = datetime.datetime.now() # date.strftime('%Y-%m-%d %H:%M:%S')
        self.archivos = archivos if archivos else {}
        self.anterior = anterior

    def agregar_archivo(self, archivo):
        self.archivos.append(archivo)

    def __str__(self):
        archivos = ""
        for archivo in self.archivos:
            archivos += "\t/"+archivo+"\n"
        return f"Commit {self.id}: {self.msj_commit} por {self.author} en {self.date.strftime('%Y-%m-%d %H:%M:%S')} / commit anterior: {self.anterior}\nArchivos: \n{archivos}"