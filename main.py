from repositorio import Repositorio
import time
# Inicializar el repositorio
def main():
    repo = Repositorio()
    print("Cargando Repositorio...")
    time.sleep(3)
    print("1 -> Hacer un commit\n2 -> Crear rama\n3 -> Cambiar rama\n4 -> Hacer un merge\n5 -> Mostrar ramas\n6 -> Mostrar historial de la rama actual\n0 -> Finalizar")
    while True:
        try:
            opcion = int(input(f"\nIndique el numero de su accion ({repo.ramas[repo.index].nombre_rama}): "))
            match opcion:
                case 1:
                    repo.hacer_commit(input("Mensaje del commit: "))
                case 2:
                    while True:
                        try:
                            nombre_rama = input("Nombre de la rama: ")
                            if not nombre_rama.strip():
                                raise ValueError("El nombre de la rama no puede estar vacío.")
                            elif not nombre_rama.isalnum():
                                raise ValueError("El nombre de la rama solo puede contener letras y números.")
                            elif nombre_rama in [rama.nombre_rama for rama in repo.ramas]:
                                raise ValueError("La rama ya existe. Por favor, ingrese un nombre diferente.")
                            repo.crear_rama(nombre_rama)
                            print("Rama creada con éxito.")
                            break
                        except ValueError as e:
                            print(f"Error: {e}")
                case 3:
                    rama_cambio = input("Nombre de la rama a cambiar a: ")
                    if repo.cambiar_rama(rama_cambio):
                        repo.cambiar_rama(rama_cambio)
                        print(f"Se cambió a la rama {rama_cambio}")
                    else:
                        print(f"No se encontró la rama {rama_cambio}")
                case 4:
                    rama_a_unir = input(f"Unir {repo.ramas[repo.index].nombre_rama} con: ")
                    nombres_de_ramasy = [rama.nombre_rama for rama in repo.ramas]
                    if rama_a_unir in nombres_de_ramasy:
                        repo.merge(rama_a_unir)
                        print(f"Se realizó el merge con la rama {rama_a_unir}")
                    else:
                        print(f"La rama {rama_a_unir} no existe en el repositorio")
                case 5:
                    repo.mostrar_ramas()
                case 6:
                    repo.mostrar_historial()
                case 0:
                    # Agregar archivos y hacer commits
                    # repo.hacer_commit("Initial commit")
                    # repo.hacer_commit("commit final")
                    # # Crear una nueva rama y trabajar en ella
                    # repo.crear_rama("develop")
                    # repo.cambiar_rama("develop")
                    # repo.hacer_commit("Added new feature")
                    # # Cambiar a la rama principal y hacer un merge
                    # repo.cambiar_rama("main")
                    # repo.merge("develop")
                    # # Mostrar el historial de commits
                    # repo.mostrar_historial()

                    # repo.cambiar_rama("develop")
                    break
        except ValueError as e:
            print(f"Error: {e}")
main()
            
"""
"""