"""
Sistema de Simulación Git
Universidad José Antonio Paez
Facultad de Ingeniería
Escuela de Ingeniería en Computación

Este programa simula un sistema Git utilizando estructuras de datos como
listas enlazadas, pilas y colas para implementar las funcionalidades básicas
de un sistema de control de versiones.
"""

import os
import json
import hashlib
import datetime
from typing import List, Dict, Optional, Any
import re
import time
import random

# Configuración para habilitar/deshabilitar comandos
CONFIG_FILE = "config.json"

class Node:
    """Clase base para nodos en estructuras de datos enlazadas"""
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    """Implementación de lista enlazada"""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def append(self, data):
        """Añade un elemento al final de la lista"""
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1
        return new_node
    
    def get_size(self):
        """Retorna el tamaño de la lista"""
        return self.size
    
    def is_empty(self):
        """Verifica si la lista está vacía"""
        return self.head is None
    
    def find(self, key, value):
        """Busca un elemento en la lista por un atributo específico"""
        current = self.head
        while current:
            if hasattr(current.data, key) and getattr(current.data, key) == value:
                return current.data
            current = current.next
        return None
    
    def to_list(self):
        """Convierte la lista enlazada a una lista de Python"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

class Stack:
    """Implementación de pila utilizando lista enlazada"""
    def __init__(self):
        self.items = LinkedList()
    
    def push(self, item):
        """Añade un elemento a la pila"""
        self.items.append(item)
    
    def pop(self):
        """Elimina y retorna el elemento superior de la pila"""
        if self.is_empty():
            return None
        
        if self.items.head == self.items.tail:
            item = self.items.head.data
            self.items.head = None
            self.items.tail = None
            self.items.size -= 1
            return item
        
        current = self.items.head
        while current.next != self.items.tail:
            current = current.next
        
        item = self.items.tail.data
        self.items.tail = current
        current.next = None
        self.items.size -= 1
        return item
    
    def peek(self):
        """Retorna el elemento superior sin eliminarlo"""
        if self.is_empty():
            return None
        return self.items.tail.data
    
    def is_empty(self):
        """Verifica si la pila está vacía"""
        return self.items.is_empty()
    
    def size(self):
        """Retorna el tamaño de la pila"""
        return self.items.get_size()
    
    def to_list(self):
        """Convierte la pila a una lista de Python"""
        return self.items.to_list()

class Queue:
    """Implementación de cola utilizando lista enlazada"""
    def __init__(self):
        self.items = LinkedList()
    
    def enqueue(self, item):
        """Añade un elemento al final de la cola"""
        self.items.append(item)
    
    def dequeue(self):
        """Elimina y retorna el primer elemento de la cola"""
        if self.is_empty():
            return None
        
        item = self.items.head.data
        self.items.head = self.items.head.next
        self.items.size -= 1
        
        if self.items.head is None:
            self.items.tail = None
            
        return item
    
    def peek(self):
        """Retorna el primer elemento sin eliminarlo"""
        if self.is_empty():
            return None
        return self.items.head.data
    
    def is_empty(self):
        """Verifica si la cola está vacía"""
        return self.items.is_empty()
    
    def size(self):
        """Retorna el tamaño de la cola"""
        return self.items.get_size()
    
    def to_list(self):
        """Convierte la cola a una lista de Python"""
        return self.items.to_list()
    
    def find(self, key, value):
        """Busca un elemento en la cola por un atributo específico"""
        return self.items.find(key, value)

class File:
    """Clase que representa un archivo en el sistema Git"""
    def __init__(self, name: str, content: str = "", status: str = "A"):
        self.name = name
        self.content = content
        self.status = status  # A: Added, M: Modified, D: Deleted
        self.checksum = self._calculate_checksum()
        self.path = name  # Simplificado para este ejemplo
    
    def _calculate_checksum(self) -> str:
        """Calcula el checksum SHA-1 del contenido del archivo"""
        return hashlib.sha1(self.content.encode()).hexdigest()
    
    def update_content(self, new_content: str):
        """Actualiza el contenido del archivo y recalcula el checksum"""
        self.content = new_content
        self.status = "M"
        self.checksum = self._calculate_checksum()
    
    def mark_as_deleted(self):
        """Marca el archivo como eliminado"""
        self.status = "D"
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para serialización"""
        return {
            "name": self.name,
            "content": self.content,
            "status": self.status,
            "checksum": self.checksum,
            "path": self.path
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'File':
        """Crea un objeto File desde un diccionario"""
        file = cls(data["name"], data["content"], data["status"])
        file.checksum = data["checksum"]
        file.path = data["path"]
        return file

class Commit:
    """Clase que representa un commit en el sistema Git"""
    def __init__(self, message: str, author_email: str, branch_name: str = "main"):
        self.id = self._generate_id()
        self.timestamp = datetime.datetime.now().isoformat()
        self.author_email = author_email
        self.message = message
        self.parent_id = None
        self.files = []  # Lista de archivos modificados
        self.branch_name = branch_name
    
    def _generate_id(self) -> str:
        """Genera un ID único para el commit (simulando SHA-1)"""
        timestamp = str(datetime.datetime.now().timestamp())
        random_str = str(random.random())
        return hashlib.sha1((timestamp + random_str).encode()).hexdigest()[:10]
    
    def add_file(self, file: File):
        """Añade un archivo al commit"""
        self.files.append(file.to_dict())
    
    def set_parent(self, parent_id: str):
        """Establece el ID del commit padre"""
        self.parent_id = parent_id
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para serialización"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "author_email": self.author_email,
            "message": self.message,
            "parent_id": self.parent_id,
            "files": self.files,
            "branch_name": self.branch_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Commit':
        """Crea un objeto Commit desde un diccionario"""
        commit = cls(data["message"], data["author_email"], data["branch_name"])
        commit.id = data["id"]
        commit.timestamp = data["timestamp"]
        commit.parent_id = data["parent_id"]
        commit.files = data["files"]
        return commit

class Branch:
    """Clase que representa una rama en el sistema Git"""
    def __init__(self, name: str, head_commit_id: Optional[str] = None):
        self.name = name
        self.head_commit_id = head_commit_id
    
    def update_head(self, commit_id: str):
        """Actualiza el commit head de la rama"""
        self.head_commit_id = commit_id
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para serialización"""
        return {
            "name": self.name,
            "head_commit_id": self.head_commit_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Branch':
        """Crea un objeto Branch desde un diccionario"""
        return cls(data["name"], data["head_commit_id"])

class PullRequest:
    """Clase que representa un pull request en el sistema Git"""
    def __init__(self, title: str, description: str, author: str, 
                 source_branch: str, target_branch: str):
        self.id = self._generate_id()
        self.title = title
        self.description = description
        self.author = author
        self.created_at = datetime.datetime.now().isoformat()
        self.source_branch = source_branch
        self.target_branch = target_branch
        self.commits = []  # Lista de IDs de commits asociados
        self.modified_files = []  # Lista de archivos modificados
        self.reviewers = []  # Lista de revisores asignados
        self.closed_at = None  # Fecha de cierre o fusión
        self.status = "pending"  # pending, reviewing, approved, merged, rejected
        self.tags = []  # Etiquetas asignadas
    
    def _generate_id(self) -> str:
        """Genera un ID único para el pull request"""
        timestamp = str(datetime.datetime.now().timestamp())
        random_str = str(random.random())
        return hashlib.sha1((timestamp + random_str).encode()).hexdigest()[:8]
    
    def add_commit(self, commit_id: str):
        """Añade un commit al pull request"""
        if commit_id not in self.commits:
            self.commits.append(commit_id)
    
    def add_modified_file(self, file_path: str):
        """Añade un archivo modificado al pull request"""
        if file_path not in self.modified_files:
            self.modified_files.append(file_path)
    
    def add_reviewer(self, reviewer: str):
        """Añade un revisor al pull request"""
        if reviewer not in self.reviewers:
            self.reviewers.append(reviewer)
    
    def update_status(self, status: str):
        """Actualiza el estado del pull request"""
        valid_statuses = ["pending", "reviewing", "approved", "merged", "rejected"]
        if status in valid_statuses:
            self.status = status
            if status in ["merged", "rejected"]:
                self.closed_at = datetime.datetime.now().isoformat()
    
    def add_tag(self, tag: str):
        """Añade una etiqueta al pull request"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para serialización"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at,
            "source_branch": self.source_branch,
            "target_branch": self.target_branch,
            "commits": self.commits,
            "modified_files": self.modified_files,
            "reviewers": self.reviewers,
            "closed_at": self.closed_at,
            "status": self.status,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PullRequest':
        """Crea un objeto PullRequest desde un diccionario"""
        pr = cls(
            data["title"], 
            data["description"], 
            data["author"], 
            data["source_branch"], 
            data["target_branch"]
        )
        pr.id = data["id"]
        pr.created_at = data["created_at"]
        pr.commits = data["commits"]
        pr.modified_files = data["modified_files"]
        pr.reviewers = data["reviewers"]
        pr.closed_at = data["closed_at"]
        pr.status = data["status"]
        pr.tags = data["tags"]
        return pr

class Repository:
    """Clase que representa un repositorio Git"""
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.commits = LinkedList()  # Lista enlazada de commits
        self.staging_area = Stack()  # Pila para el área de staging
        self.pull_requests = Queue()  # Cola para pull requests
        self.branches = []  # Lista de ramas
        self.current_branch = "main"  # Rama actual
        self.files = {}  # Diccionario de archivos en el repositorio
        
        # Crear rama principal
        self.branches.append(Branch("main"))
    
    def get_branch(self, name: str) -> Optional[Branch]:
        """Obtiene una rama por su nombre"""
        for branch in self.branches:
            if branch.name == name:
                return branch
        return None
    
    def get_current_branch(self) -> Branch:
        """Obtiene la rama actual"""
        return self.get_branch(self.current_branch)
    
    def add_file_to_staging(self, file: File):
        """Añade un archivo al área de staging"""
        self.staging_area.push(file)
        # Actualizar o añadir el archivo al repositorio
        self.files[file.name] = file
    
    def create_commit(self, message: str, author_email: str) -> Optional[Commit]:
        """Crea un nuevo commit con los archivos en el área de staging"""
        if self.staging_area.is_empty():
            print("No hay archivos en el área de staging para hacer commit.")
            return None
        
        # Crear nuevo commit
        commit = Commit(message, author_email, self.current_branch)
        
        # Obtener el ID del commit padre (último commit de la rama actual)
        current_branch = self.get_current_branch()
        if current_branch.head_commit_id:
            commit.set_parent(current_branch.head_commit_id)
        
        # Añadir archivos del área de staging al commit
        staged_files = []
        while not self.staging_area.is_empty():
            file = self.staging_area.pop()
            commit.add_file(file)
            staged_files.append(file)
        
        # Añadir el commit a la lista de commits
        self.commits.append(commit)
        
        # Actualizar el head de la rama actual
        current_branch.update_head(commit.id)
        
        return commit
    
    def checkout_branch(self, branch_name: str) -> bool:
        """Cambia a una rama específica"""
        branch = self.get_branch(branch_name)
        if not branch:
            print(f"La rama '{branch_name}' no existe.")
            return False
        
        self.current_branch = branch_name
        return True
    
    def create_branch(self, branch_name: str) -> bool:
        """Crea una nueva rama"""
        if self.get_branch(branch_name):
            print(f"La rama '{branch_name}' ya existe.")
            return False
        
        # Obtener el commit actual como punto de partida para la nueva rama
        current_branch = self.get_current_branch()
        head_commit_id = current_branch.head_commit_id if current_branch else None
        
        # Crear la nueva rama
        new_branch = Branch(branch_name, head_commit_id)
        self.branches.append(new_branch)
        
        return True
    
    def get_commit_by_id(self, commit_id: str) -> Optional[Commit]:
        """Obtiene un commit por su ID"""
        current = self.commits.head
        while current:
            if current.data.id == commit_id:
                return current.data
            current = current.next
        return None
    
    def checkout_commit(self, commit_id: str) -> bool:
        """Cambia al estado de un commit específico"""
        commit = self.get_commit_by_id(commit_id)
        if not commit:
            print(f"El commit '{commit_id}' no existe.")
            return False
        
        # Crear una rama temporal para el commit
        temp_branch_name = f"temp-{commit_id[:6]}"
        self.create_branch(temp_branch_name)
        
        # Actualizar el head de la rama temporal
        temp_branch = self.get_branch(temp_branch_name)
        temp_branch.update_head(commit_id)
        
        # Cambiar a la rama temporal
        self.checkout_branch(temp_branch_name)
        
        return True
    
    def create_pull_request(self, title: str, description: str, author: str,
                           source_branch: str, target_branch: str) -> Optional[PullRequest]:
        """Crea un nuevo pull request"""
        # Verificar que las ramas existen
        if not self.get_branch(source_branch):
            print(f"La rama de origen '{source_branch}' no existe.")
            return None
        
        if not self.get_branch(target_branch):
            print(f"La rama de destino '{target_branch}' no existe.")
            return None
        
        # Crear el pull request
        pr = PullRequest(title, description, author, source_branch, target_branch)
        
        # Añadir commits de la rama de origen que no están en la rama de destino
        source_branch_obj = self.get_branch(source_branch)
        target_branch_obj = self.get_branch(target_branch)
        
        if source_branch_obj.head_commit_id:
            pr.add_commit(source_branch_obj.head_commit_id)
        
        # Añadir el pull request a la cola
        self.pull_requests.enqueue(pr)
        
        return pr
    
    def review_pull_request(self, pr_id: str, reviewer: str) -> bool:
        """Revisa un pull request"""
        pr = self.pull_requests.find("id", pr_id)
        if not pr:
            print(f"El pull request '{pr_id}' no existe.")
            return False
        
        pr.add_reviewer(reviewer)
        pr.update_status("reviewing")
        return True
    
    def approve_pull_request(self, pr_id: str) -> bool:
        """Aprueba un pull request"""
        pr = self.pull_requests.find("id", pr_id)
        if not pr:
            print(f"El pull request '{pr_id}' no existe.")
            return False
        
        pr.update_status("approved")
        return True
    
    def reject_pull_request(self, pr_id: str) -> bool:
        """Rechaza un pull request"""
        pr = self.pull_requests.find("id", pr_id)
        if not pr:
            print(f"El pull request '{pr_id}' no existe.")
            return False
        
        pr.update_status("rejected")
        return True
    
    def merge_pull_request(self, pr_id: str) -> bool:
        """Fusiona un pull request aprobado"""
        pr = self.pull_requests.find("id", pr_id)
        if not pr:
            print(f"El pull request '{pr_id}' no existe.")
            return False
        
        if pr.status != "approved":
            print(f"El pull request '{pr_id}' no está aprobado.")
            return False
        
        # Implementación simplificada de la fusión
        pr.update_status("merged")
        
        # Actualizar la rama de destino para que apunte al último commit de la rama de origen
        source_branch = self.get_branch(pr.source_branch)
        target_branch = self.get_branch(pr.target_branch)
        
        if source_branch and target_branch and source_branch.head_commit_id:
            target_branch.update_head(source_branch.head_commit_id)
        
        return True
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para serialización"""
        return {
            "name": self.name,
            "path": self.path,
            "commits": [commit.to_dict() for commit in self.commits.to_list()],
            "branches": [branch.to_dict() for branch in self.branches],
            "current_branch": self.current_branch,
            "files": {name: file.to_dict() for name, file in self.files.items()},
            "pull_requests": [pr.to_dict() for pr in self.pull_requests.to_list()]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Repository':
        """Crea un objeto Repository desde un diccionario"""
        repo = cls(data["name"], data["path"])
        
        # Cargar ramas
        repo.branches = []
        for branch_data in data["branches"]:
            repo.branches.append(Branch.from_dict(branch_data))
        
        # Cargar rama actual
        repo.current_branch = data["current_branch"]
        
        # Cargar archivos
        repo.files = {}
        for name, file_data in data["files"].items():
            repo.files[name] = File.from_dict(file_data)
        
        # Cargar commits
        for commit_data in data["commits"]:
            repo.commits.append(Commit.from_dict(commit_data))
        
        # Cargar pull requests
        for pr_data in data["pull_requests"]:
            repo.pull_requests.enqueue(PullRequest.from_dict(pr_data))
        
        return repo

class GitSystem:
    """Clase principal que gestiona el sistema Git"""
    def __init__(self):
        self.repositories = LinkedList()
        self.current_repository = None
        self.user_email = "usuario@example.com"  # Email por defecto
        self.commands = self._load_commands()
        
        # Cargar datos si existen
        self._load_data()
    
    def _load_commands(self) -> Dict[str, bool]:
        """Carga la configuración de comandos habilitados/deshabilitados"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Configuración por defecto (todos los comandos habilitados)
        return {
            "init": True,
            "status": True,
            "log": True,
            "add": True,
            "commit": True,
            "checkout": True,
            "branch": True,
            "pr": True
        }
    
    def _save_commands(self):
        """Guarda la configuración de comandos"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.commands, f, indent=2)
    
    def _load_data(self):
        """Carga los datos del sistema desde archivos JSON"""
        if os.path.exists("repositories.json"):
            try:
                with open("repositories.json", 'r') as f:
                    repos_data = json.load(f)
                    for repo_data in repos_data:
                        self.repositories.append(Repository.from_dict(repo_data))
            except Exception as e:
                print(f"Error al cargar los datos: {e}")
    
    def _save_data(self):
        """Guarda los datos del sistema en archivos JSON"""
        repos_data = [repo.to_dict() for repo in self.repositories.to_list()]
        with open("repositories.json", 'w') as f:
            json.dump(repos_data, f, indent=2)
    
    def is_command_enabled(self, command: str) -> bool:
        """Verifica si un comando está habilitado"""
        return self.commands.get(command, False)
    
    def enable_command(self, command: str):
        """Habilita un comando"""
        self.commands[command] = True
        self._save_commands()
    
    def disable_command(self, command: str):
        """Deshabilita un comando"""
        self.commands[command] = False
        self._save_commands()
    
    def get_repository(self, name: str) -> Optional[Repository]:
        """Obtiene un repositorio por su nombre"""
        current = self.repositories.head
        while current:
            if current.data.name == name:
                return current.data
            current = current.next
        return None
    
    def create_repository(self, name: str, path: str) -> Repository:
        """Crea un nuevo repositorio"""
        # Verificar si ya existe un repositorio con ese nombre
        if self.get_repository(name):
            raise ValueError(f"Ya existe un repositorio con el nombre '{name}'")
        
        # Crear el repositorio
        repo = Repository(name, path)
        self.repositories.append(repo)
        self.current_repository = repo
        
        # Guardar los datos
        self._save_data()
        
        return repo
    
    def set_current_repository(self, name: str) -> bool:
        """Establece el repositorio actual"""
        repo = self.get_repository(name)
        if repo:
            self.current_repository = repo
            return True
        return False
    
    def list_repositories(self) -> List[str]:
        """Lista los nombres de todos los repositorios"""
        return [repo.name for repo in self.repositories.to_list()]
    
    def set_user_email(self, email: str):
        """Establece el email del usuario"""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Email inválido")
        self.user_email = email
    
    def execute_command(self, command: str, args: List[str]) -> Any:
        """Ejecuta un comando Git"""
        if not self.is_command_enabled(command):
            print(f"El comando '{command}' está deshabilitado.")
            return None
        
        # Comandos que no requieren un repositorio actual
        if command == "init":
            if len(args) < 1:
                print("Uso: git init <nombre_repositorio>")
                return None
            
            repo_name = args[0]
            repo_path = f"./{repo_name}"
            return self.create_repository(repo_name, repo_path)
        
        # Verificar si hay un repositorio actual
        if not self.current_repository:
            print("No hay un repositorio seleccionado. Use 'git init' o seleccione uno existente.")
            return None
        
        # Comandos que requieren un repositorio actual
        if command == "status":
            return self._git_status()
        elif command == "log":
            return self._git_log()
        elif command == "add":
            if len(args) < 1:
                print("Uso: git add <archivo>")
                return None
            return self._git_add(args[0])
        elif command == "commit":
            if len(args) < 2 or args[0] != "-m":
                print("Uso: git commit -m \"<mensaje>\"")
                return None
            return self._git_commit(args[1])
        elif command == "checkout":
            if len(args) < 1:
                print("Uso: git checkout <rama_o_commit>")
                return None
            return self._git_checkout(args[0])
        elif command == "branch":
            if len(args) < 1:
                # Listar ramas
                return [branch.name for branch in self.current_repository.branches]
            # Crear rama
            return self._git_branch(args[0])
        elif command == "pr":
            if len(args) < 1:
                print("Uso: git pr <subcomando> [argumentos]")
                return None
            
            subcommand = args[0]
            if subcommand == "create":
                if len(args) < 3:
                    print("Uso: git pr create <rama_origen> <rama_destino>")
                    return None
                return self._git_pr_create(args[1], args[2])
            elif subcommand == "status":
                return self._git_pr_status()
            elif subcommand == "review":
                if len(args) < 2:
                    print("Uso: git pr review <id_pr>")
                    return None
                return self._git_pr_review(args[1])
            elif subcommand == "approve":
                if len(args) < 2:
                    print("Uso: git pr approve <id_pr>")
                    return None
                return self._git_pr_approve(args[1])
            elif subcommand == "reject":
                if len(args) < 2:
                    print("Uso: git pr reject <id_pr>")
                    return None
                return self._git_pr_reject(args[1])
            elif subcommand == "cancel":
                if len(args) < 2:
                    print("Uso: git pr cancel <id_pr>")
                    return None
                return self._git_pr_cancel(args[1])
            elif subcommand == "list":
                return self._git_pr_list()
            elif subcommand == "next":
                return self._git_pr_next()
            elif subcommand == "tag":
                if len(args) < 3:
                    print("Uso: git pr tag <id_pr> <etiqueta>")
                    return None
                return self._git_pr_tag(args[1], args[2])
            elif subcommand == "clear":
                return self._git_pr_clear()
            else:
                print(f"Subcomando de PR desconocido: {subcommand}")
                return None
        else:
            print(f"Comando desconocido: {command}")
            return None
    
    def _git_status(self) -> Dict:
        """Implementa el comando git status"""
        repo = self.current_repository
        
        # Obtener archivos en el área de staging
        staged_files = repo.staging_area.to_list()
        
        # Obtener información de la rama actual
        current_branch = repo.get_current_branch()
        
        return {
            "branch": repo.current_branch,
            "staged_files": [file.to_dict() for file in staged_files],
            "modified_files": [file.to_dict() for name, file in repo.files.items() 
                              if file.status == "M" and file not in staged_files],
            "untracked_files": [file.to_dict() for name, file in repo.files.items() 
                               if file.status == "A" and file not in staged_files]
        }
    
    def _git_log(self) -> List[Dict]:
        """Implementa el comando git log"""
        commits = self.current_repository.commits.to_list()
        return [commit.to_dict() for commit in commits]
    
    def _git_add(self, file_path: str) -> bool:
        """Implementa el comando git add"""
        repo = self.current_repository
        
        # Verificar si el archivo ya existe en el repositorio
        if file_path in repo.files:
            file = repo.files[file_path]
        else:
            # Crear un nuevo archivo (simulado)
            file = File(file_path, f"Contenido simulado para {file_path}")
        
        # Añadir el archivo al área de staging
        repo.add_file_to_staging(file)
        
        # Guardar los datos
        self._save_data()
        
        return True
    
    def _git_commit(self, message: str) -> Optional[Dict]:
        """Implementa el comando git commit"""
        repo = self.current_repository
        
        # Crear el commit
        commit = repo.create_commit(message, self.user_email)
        if not commit:
            return None
        
        # Guardar los datos
        self._save_data()
        
        return commit.to_dict()
    
    def _git_checkout(self, target: str) -> bool:
        """Implementa el comando git checkout"""
        repo = self.current_repository
        
        # Verificar si es una rama o un commit
        if repo.get_branch(target):
            # Es una rama
            result = repo.checkout_branch(target)
        else:
            # Intentar como commit
            result = repo.checkout_commit(target)
        
        # Guardar los datos
        if result:
            self._save_data()
        
        return result
    
    def _git_branch(self, branch_name: str) -> bool:
        """Implementa el comando git branch"""
        result = self.current_repository.create_branch(branch_name)
        
        # Guardar los datos
        if result:
            self._save_data()
        
        return result
    
    def _git_pr_create(self, source_branch: str, target_branch: str) -> Optional[Dict]:
        """Implementa el comando git pr create"""
        repo = self.current_repository
        
        # Solicitar título y descripción
        title = input("Título del Pull Request: ")
        description = input("Descripción del Pull Request: ")
        
        # Crear el pull request
        pr = repo.create_pull_request(title, description, self.user_email, 
                                     source_branch, target_branch)
        
        # Guardar los datos
        if pr:
            self._save_data()
            return pr.to_dict()
        
        return None
    
    def _git_pr_status(self) -> Dict:
        """Implementa el comando git pr status"""
        prs = self.current_repository.pull_requests.to_list()
        
        # Agrupar por estado
        result = {
            "pending": [],
            "reviewing": [],
            "approved": [],
            "merged": [],
            "rejected": []
        }
        
        for pr in prs:
            if pr.status in result:
                result[pr.status].append(pr.to_dict())
        
        return result
    
    def _git_pr_review(self, pr_id: str) -> bool:
        """Implementa el comando git pr review"""
        reviewer = input("Nombre del revisor: ")
        result = self.current_repository.review_pull_request(pr_id, reviewer)
        
        # Guardar los datos
        if result:
            self._save_data()
        
        return result
    
    def _git_pr_approve(self, pr_id: str) -> bool:
        """Implementa el comando git pr approve"""
        result = self.current_repository.approve_pull_request(pr_id)
        
        # Guardar los datos
        if result:
            self._save_data()
        
        return result
    
    def _git_pr_reject(self, pr_id: str) -> bool:
        """Implementa el comando git pr reject"""
        result = self.current_repository.reject_pull_request(pr_id)
        
        # Guardar los datos
        if result:
            self._save_data()
        
        return result
    
    def _git_pr_cancel(self, pr_id: str) -> bool:
        """Implementa el comando git pr cancel"""
        # Buscar el PR en la cola
        pr = self.current_repository.pull_requests.find("id", pr_id)
        if not pr:
            print(f"El pull request '{pr_id}' no existe.")
            return False
        
        # Implementación simplificada: marcar como rechazado
        pr.update_status("rejected")
        
        # Guardar los datos
        self._save_data()
        
        return True
    
    def _git_pr_list(self) -> List[Dict]:
        """Implementa el comando git pr list"""
        prs = self.current_repository.pull_requests.to_list()
        return [pr.to_dict() for pr in prs]
    
    def _git_pr_next(self) -> Optional[Dict]:
        """Implementa el comando git pr next"""
        # Obtener el siguiente PR pendiente
        prs = self.current_repository.pull_requests.to_list()
        for pr in prs:
            if pr.status == "pending":
                pr.update_status("reviewing")
                
                # Guardar los datos
                self._save_data()
                
                return pr.to_dict()
        
        print("No hay pull requests pendientes.")
        return None
    
    def _git_pr_tag(self, pr_id: str, tag: str) -> bool:
        """Implementa el comando git pr tag"""
        pr = self.current_repository.pull_requests.find("id", pr_id)
        if not pr:
            print(f"El pull request '{pr_id}' no existe.")
            return False
        
        pr.add_tag(tag)
        
        # Guardar los datos
        self._save_data()
        
        return True
    
    def _git_pr_clear(self) -> bool:
        """Implementa el comando git pr clear"""
        # Implementación simplificada: crear una nueva cola vacía
        self.current_repository.pull_requests = Queue()
        
        # Guardar los datos
        self._save_data()
        
        return True

def main():
    """Función principal del programa"""
    git_system = GitSystem()
    
    # Cargar datos de prueba si no hay repositorios
    if git_system.repositories.is_empty():
        _load_test_data(git_system)
    
    print("Sistema de Simulación Git")
    print("=========================")
    
    while True:
        # Mostrar el repositorio actual
        if git_system.current_repository:
            prompt = f"[{git_system.current_repository.name}] git> "
        else:
            prompt = "git> "
        
        # Leer comando
        command_line = input(prompt)
        if not command_line:
            continue
        
        # Salir del programa
        if command_line.lower() in ["exit", "quit", "q"]:
            break
        
        # Parsear el comando
        parts = command_line.split()
        command = parts[0]
        args = parts[1:]
        
        # Comandos especiales del sistema
        if command == "repos":
            # Listar repositorios
            repos = git_system.list_repositories()
            if repos:
                print("Repositorios disponibles:")
                for repo in repos:
                    print(f"  - {repo}")
            else:
                print("No hay repositorios. Use 'git init <nombre>' para crear uno.")
            continue
        elif command == "use":
            # Seleccionar repositorio
            if len(args) < 1:
                print("Uso: use <nombre_repositorio>")
                continue
            
            if git_system.set_current_repository(args[0]):
                print(f"Repositorio actual: {args[0]}")
            else:
                print(f"El repositorio '{args[0]}' no existe.")
            continue
        elif command == "email":
            # Establecer email del usuario
            if len(args) < 1:
                print(f"Email actual: {git_system.user_email}")
                continue
            
            try:
                git_system.set_user_email(args[0])
                print(f"Email establecido: {args[0]}")
            except ValueError as e:
                print(f"Error: {e}")
            continue
        elif command == "enable":
            # Habilitar comando
            if len(args) < 1:
                print("Uso: enable <comando>")
                continue
            
            git_system.enable_command(args[0])
            print(f"Comando '{args[0]}' habilitado.")
            continue
        elif command == "disable":
            # Deshabilitar comando
            if len(args) < 1:
                print("Uso: disable <comando>")
                continue
            
            git_system.disable_command(args[0])
            print(f"Comando '{args[0]}' deshabilitado.")
            continue
        elif command == "help":
            # Mostrar ayuda
            _show_help()
            continue
        
        # Ejecutar comando Git
        try:
            result = git_system.execute_command(command, args)
            
            # Mostrar resultado
            if result is not None:
                if isinstance(result, dict):
                    _print_dict(result)
                elif isinstance(result, list):
                    _print_list(result)
                elif isinstance(result, bool):
                    if result:
                        print("Operación completada con éxito.")
                    else:
                        print("La operación no se pudo completar.")
                else:
                    print(result)
        except Exception as e:
            print(f"Error: {e}")

def _print_dict(data, indent=0):
    """Imprime un diccionario de forma legible"""
    for key, value in data.items():
        if isinstance(value, dict):
            print(" " * indent + f"{key}:")
            _print_dict(value, indent + 2)
        elif isinstance(value, list):
            print(" " * indent + f"{key}:")
            _print_list(value, indent + 2)
        else:
            print(" " * indent + f"{key}: {value}")

def _print_list(data, indent=0):
    """Imprime una lista de forma legible"""
    if not data:
        print(" " * indent + "(vacío)")
        return
    
    for i, item in enumerate(data):
        if isinstance(item, dict):
            print(" " * indent + f"[{i}]:")
            _print_dict(item, indent + 2)
        elif isinstance(item, list):
            print(" " * indent + f"[{i}]:")
            _print_list(item, indent + 2)
        else:
            print(" " * indent + f"[{i}]: {item}")

def _show_help():
    """Muestra la ayuda del programa"""
    print("\nAyuda del Sistema de Simulación Git")
    print("==================================")
    print("\nComandos del sistema:")
    print("  repos                  - Lista los repositorios disponibles")
    print("  use <repo>             - Selecciona un repositorio")
    print("  email [nuevo_email]    - Muestra o establece el email del usuario")
    print("  enable <comando>       - Habilita un comando Git")
    print("  disable <comando>      - Deshabilita un comando Git")
    print("  help                   - Muestra esta ayuda")
    print("  exit, quit, q          - Sale del programa")
    
    print("\nComandos Git:")
    print("  git init <nombre>      - Crea un nuevo repositorio")
    print("  git status             - Muestra el estado del repositorio")
    print("  git log                - Muestra el historial de commits")
    print("  git add <archivo>      - Añade un archivo al área de staging")
    print("  git commit -m \"msg\"    - Crea un nuevo commit con los archivos en staging")
    print("  git checkout <rama>    - Cambia a una rama específica")
    print("  git branch <nombre>    - Crea una nueva rama")
    
    print("\nComandos de Pull Request:")
    print("  git pr create <origen> <destino> - Crea un nuevo pull request")
    print("  git pr status          - Muestra el estado de los pull requests")
    print("  git pr review <id>     - Revisa un pull request")
    print("  git pr approve <id>    - Aprueba un pull request")
    print("  git pr reject <id>     - Rechaza un pull request")
    print("  git pr cancel <id>     - Cancela un pull request")
    print("  git pr list            - Lista todos los pull requests")
    print("  git pr next            - Procesa el siguiente pull request pendiente")
    print("  git pr tag <id> <tag>  - Asigna una etiqueta a un pull request")
    print("  git pr clear           - Elimina todos los pull requests pendientes")

def _load_test_data(git_system):
    """Carga datos de prueba en el sistema"""
    # Crear un repositorio de prueba
    repo = git_system.create_repository("proyecto-test", "./proyecto-test")
    
    # Añadir algunos archivos
    git_system.execute_command("add", ["README.md"])
    git_system.execute_command("add", ["main.py"])
    git_system.execute_command("add", ["utils.py"])
    
    # Crear un commit inicial
    git_system.execute_command("commit", ["-m", "Commit inicial"])
    
    # Crear una rama de desarrollo
    git_system.execute_command("branch", ["desarrollo"])
    
    # Cambiar a la rama de desarrollo
    git_system.execute_command("checkout", ["desarrollo"])
    
    # Añadir más archivos en la rama de desarrollo
    git_system.execute_command("add", ["feature.py"])
    git_system.execute_command("commit", ["-m", "Añadir nueva característica"])
    
    # Crear un pull request
    git_system.current_repository.create_pull_request(
        "Implementación de nueva característica",
        "Esta PR añade una nueva característica al proyecto",
        git_system.user_email,
        "desarrollo",
        "main"
    )
    
    # Volver a la rama principal
    git_system.execute_command("checkout", ["main"])
    
    print("Datos de prueba cargados correctamente.")

if __name__ == "__main__":
    main()