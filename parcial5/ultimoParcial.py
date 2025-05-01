import os
import json
import hashlib
import datetime
import difflib
import pickle
from typing import List, Dict, Optional, Any, Tuple
import re
import time
import random

# Configuración del sistema
DATA_DIR = "data"  # Directorio para almacenar los archivos JSON
REPOS_FILE = os.path.join(DATA_DIR, "repositories_index.json")  # Índice de repositorios

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

# 1. MÓDULO DE GESTIÓN DE BRANCHES (ÁRBOL N-ARIO)
class BranchNode:
    """Nodo para el árbol n-ario de ramas"""
    def __init__(self, name: str, head_commit_id: Optional[str] = None):
        self.name = name
        self.head_commit_id = head_commit_id
        self.children = []  # Lista de nodos hijos (subramas)
        self.commits = LinkedList()  # Lista de commits en esta rama
    
    def add_child(self, child: 'BranchNode'):
        """Añade una subrama a esta rama"""
        self.children.append(child)
    
    def remove_child(self, branch_name: str) -> bool:
        """Elimina una subrama por su nombre"""
        for i, child in enumerate(self.children):
            if child.name == branch_name:
                self.children.pop(i)
                return True
        return False
    
    def find_child(self, branch_name: str) -> Optional['BranchNode']:
        """Busca una subrama por su nombre"""
        for child in self.children:
            if child.name == branch_name:
                return child
        return None
    
    def add_commit(self, commit: Commit):
        """Añade un commit a esta rama"""
        self.commits.append(commit)
        self.head_commit_id = commit.id
    
    def to_dict(self) -> Dict:
        """Convierte el nodo a un diccionario para serialización"""
        return {
            "name": self.name,
            "head_commit_id": self.head_commit_id,
            "children": [child.to_dict() for child in self.children],
            "commits": [commit.to_dict() for commit in self.commits.to_list()]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BranchNode':
        """Crea un nodo desde un diccionario"""
        node = cls(data["name"], data["head_commit_id"])
        
        # Cargar commits
        for commit_data in data["commits"]:
            node.commits.append(Commit.from_dict(commit_data))
        
        # Cargar hijos recursivamente
        for child_data in data["children"]:
            node.add_child(cls.from_dict(child_data))
        
        return node

class BranchTree: #1 modulo
    """Árbol n-ario para gestionar ramas de un repositorio"""
    def __init__(self):
        self.root = BranchNode("main")  # Rama principal como raíz
        self.current = self.root  # Rama actual
    
    def create_branch(self, name: str) -> bool:
        """Crea una nueva rama bajo la rama actual"""
        # Verificar si ya existe una rama con ese nombre
        if self.find_branch(name):
            print(f"La rama '{name}' ya existe.")
            return False
        
        # Crear nueva rama con el mismo head_commit_id que la rama actual
        new_branch = BranchNode(name, self.current.head_commit_id)
        self.current.add_child(new_branch)
        return True
    
    def delete_branch(self, name: str) -> bool:
        """Elimina una rama si ya ha sido fusionada"""
        # No se puede eliminar la rama principal
        if name == "main":
            print("No se puede eliminar la rama principal.")
            return False
        
        # Buscar la rama padre de la rama a eliminar
        parent, branch = self._find_branch_with_parent(name)
        if not branch:
            print(f"La rama '{name}' no existe.")
            return False
        
        # Verificar si la rama ha sido fusionada (simplificado)
        # En una implementación real, se verificaría si todos los commits
        # de la rama están presentes en otra rama
        
        # Eliminar la rama
        return parent.remove_child(name)
    
    def _find_branch_with_parent(self, name: str, node: Optional[BranchNode] = None) -> Tuple[Optional[BranchNode], Optional[BranchNode]]:
        """Busca una rama y su padre en el árbol"""
        if node is None:
            node = self.root
        
        # Buscar en los hijos directos
        for child in node.children:
            if child.name == name:
                return node, child
        
        # Buscar recursivamente en los hijos
        for child in node.children:
            parent, branch = self._find_branch_with_parent(name, child)
            if branch:
                return parent, branch
        
        return None, None
    
    def find_branch(self, name: str, node: Optional[BranchNode] = None) -> Optional[BranchNode]:
        """Busca una rama por su nombre en todo el árbol"""
        if node is None:
            node = self.root
        
        if node.name == name:
            return node
        
        # Buscar en los hijos
        for child in node.children:
            result = self.find_branch(name, child)
            if result:
                return result
        
        return None
    
    def checkout_branch(self, name: str) -> bool:
        """Cambia a una rama específica"""
        branch = self.find_branch(name)
        if not branch:
            print(f"La rama '{name}' no existe.")
            return False
        
        self.current = branch
        return True
    
    def list_branches(self):
        """Muestra todas las ramas en formato jerárquico (preorden)"""
        result = []
        self._list_branches_preorder(self.root, "", result)
        return result
    
    def _list_branches_preorder(self, node: BranchNode, prefix: str, result: List[str]):
        """Recorrido preorden del árbol de ramas"""
        branch_str = f"{prefix}{'└── ' if prefix else ''}{node.name}"
        result.append(branch_str)
        
        for i, child in enumerate(node.children):
            new_prefix = prefix + ("    " if i == len(node.children) - 1 else "│   ")
            self._list_branches_preorder(child, new_prefix, result)
    
    def merge_branches(self, source_name: str, target_name: str) -> bool:
        """Fusiona una rama en otra (postorden)"""
        source = self.find_branch(source_name)
        target = self.find_branch(target_name)
        
        if not source:
            print(f"La rama de origen '{source_name}' no existe.")
            return False
        
        if not target:
            print(f"La rama de destino '{target_name}' no existe.")
            return False
        
        # Implementar la fusión usando difflib
        # Obtener los archivos más recientes de ambas ramas
        source_files = self._get_latest_files(source)
        target_files = self._get_latest_files(target)
        
        # Fusionar los archivos
        merged_files = self._merge_files(source_files, target_files)
        
        # Crear un nuevo commit en la rama destino con los cambios fusionados
        merge_commit = Commit(
            f"Merge branch '{source_name}' into '{target_name}'",
            "system@git.local",
            target_name
        )
        
        # Añadir los archivos fusionados al commit
        for file in merged_files.values():
            merge_commit.add_file(file)
        
        # Establecer el commit padre
        if target.head_commit_id:
            merge_commit.set_parent(target.head_commit_id)
        
        # Añadir el commit a la rama destino
        target.add_commit(merge_commit)
        
        return True
    
    def _get_latest_files(self, branch: BranchNode) -> Dict[str, File]:
        """Obtiene los archivos más recientes de una rama"""
        files = {}
        
        # Recorrer los commits en orden cronológico
        for commit in branch.commits.to_list():
            for file_data in commit.files:
                file = File.from_dict(file_data)
                if file.status != "D":  # Ignorar archivos eliminados
                    files[file.name] = file
                elif file.name in files:
                    del files[file.name]
        
        return files
    
    def _merge_files(self, source_files: Dict[str, File], target_files: Dict[str, File]) -> Dict[str, File]:
        """Fusiona los archivos de dos ramas"""
        merged_files = target_files.copy()
        
        for name, source_file in source_files.items():
            if name in target_files:
                # El archivo existe en ambas ramas, usar difflib para fusionar
                target_file = target_files[name]
                
                if source_file.content != target_file.content:
                    # Crear una fusión de los contenidos
                    source_lines = source_file.content.splitlines()
                    target_lines = target_file.content.splitlines()
                    
                    # Usar difflib para obtener la diferencia
                    diff = difflib.unified_diff(
                        target_lines, source_lines, 
                        fromfile=f"{name} (target)", 
                        tofile=f"{name} (source)"
                    )
                    
                    # En una implementación real, se manejarían conflictos
                    # Aquí simplemente tomamos el contenido de la rama fuente
                    merged_file = File(name, source_file.content, "M")
                    merged_files[name] = merged_file
            else:
                # El archivo solo existe en la rama fuente, añadirlo
                merged_files[name] = source_file
        
        return merged_files
    
    def to_dict(self) -> Dict:
        """Convierte el árbol a un diccionario para serialización"""
        return {
            "root": self.root.to_dict(),
            "current": self.current.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BranchTree':
        """Crea un árbol desde un diccionario"""
        tree = cls()
        tree.root = BranchNode.from_dict(data["root"])
        
        # Establecer la rama actual
        current_name = data["current"]
        tree.current = tree.find_branch(current_name) or tree.root
        
        return tree

# 2. MÓDULO DE ADMINISTRACIÓN DE COLABORADORES (ÁRBOL BINARIO DE BÚSQUEDA)
class Collaborator:
    """Clase que representa un colaborador en el sistema Git"""
    def __init__(self, name: str, email: str, role: str = "contributor"):
        self.name = name
        self.email = email
        self.role = role
        self.contributions = 0  # Número de contribuciones
    
    def add_contribution(self):
        """Incrementa el contador de contribuciones"""
        self.contributions += 1
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para serialización"""
        return {
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "contributions": self.contributions
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Collaborator':
        """Crea un objeto Collaborator desde un diccionario"""
        collab = cls(data["name"], data["email"], data["role"])
        collab.contributions = data["contributions"]
        return collab

class BSTNode:
    """Nodo para el árbol binario de búsqueda de colaboradores"""
    def __init__(self, collaborator: Collaborator):
        self.collaborator = collaborator
        self.left = None
        self.right = None
    
    def to_dict(self) -> Dict:
        """Convierte el nodo a un diccionario para serialización"""
        result = {
            "collaborator": self.collaborator.to_dict(),
            "left": None,
            "right": None
        }
        
        if self.left:
            result["left"] = self.left.to_dict()
        
        if self.right:
            result["right"] = self.right.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> Optional['BSTNode']:
        """Crea un nodo desde un diccionario"""
        if not data:
            return None
        
        node = cls(Collaborator.from_dict(data["collaborator"]))
        
        if data["left"]:
            node.left = cls.from_dict(data["left"])
        
        if data["right"]:
            node.right = cls.from_dict(data["right"])
        
        return node

class CollaboratorsBST:
    """Árbol binario de búsqueda para gestionar colaboradores"""
    def __init__(self):
        self.root = None
    
    def add_collaborator(self, collaborator: Collaborator):
        """Añade un colaborador al árbol"""
        if not self.root:
            self.root = BSTNode(collaborator)
        else:
            self._add_collaborator_recursive(self.root, collaborator)
    
    def _add_collaborator_recursive(self, node: BSTNode, collaborator: Collaborator):
        """Añade un colaborador recursivamente"""
        # Ordenar por nombre alfabéticamente
        if collaborator.name < node.collaborator.name:
            if node.left is None:
                node.left = BSTNode(collaborator)
            else:
                self._add_collaborator_recursive(node.left, collaborator)
        else:
            if node.right is None:
                node.right = BSTNode(collaborator)
            else:
                self._add_collaborator_recursive(node.right, collaborator)
    
    def find_collaborator(self, name: str) -> Optional[Collaborator]:
        """Busca un colaborador por su nombre (inorden)"""
        result = []
        self._find_collaborator_inorder(self.root, name, result)
        return result[0] if result else None
    
    def _find_collaborator_inorder(self, node: Optional[BSTNode], name: str, result: List[Collaborator]):
        """Busca un colaborador por su nombre usando recorrido inorden"""
        if not node:
            return
        
        # Recorrido inorden: izquierda, raíz, derecha
        self._find_collaborator_inorder(node.left, name, result)
        
        # Verificar si es el colaborador buscado
        if node.collaborator.name == name:
            result.append(node.collaborator)
        
        self._find_collaborator_inorder(node.right, name, result)
    
    def remove_collaborator(self, name: str) -> bool:
        """Elimina un colaborador del árbol"""
        if not self.root:
            return False
        
        # Caso especial: eliminar la raíz
        if self.root.collaborator.name == name:
            self.root = self._remove_node(self.root)
            return True
        
        # Buscar el nodo a eliminar y su padre
        parent, node, is_left = self._find_node_and_parent(name)
        if not node:
            return False
        
        # Eliminar el nodo
        if is_left:
            parent.left = self._remove_node(node)
        else:
            parent.right = self._remove_node(node)
        
        return True
    
    def _find_node_and_parent(self, name: str) -> Tuple[Optional[BSTNode], Optional[BSTNode], bool]:
        """Busca un nodo y su padre por el nombre del colaborador"""
        if not self.root:
            return None, None, False
        
        parent = None
        current = self.root
        is_left = False
        
        while current and current.collaborator.name != name:
            parent = current
            if name < current.collaborator.name:
                current = current.left
                is_left = True
            else:
                current = current.right
                is_left = False
        
        return parent, current, is_left
    
    def _remove_node(self, node: BSTNode) -> Optional[BSTNode]:
        """Elimina un nodo y reorganiza el árbol"""
        # Caso 1: Nodo sin hijos
        if not node.left and not node.right:
            return None
        
        # Caso 2: Nodo con un solo hijo
        if not node.left:
            return node.right
        
        if not node.right:
            return node.left
        
        # Caso 3: Nodo con dos hijos
        # Encontrar el sucesor inorden (el menor valor en el subárbol derecho)
        successor_parent = node
        successor = node.right
        
        while successor.left:
            successor_parent = successor
            successor = successor.left
        
        # Reemplazar el nodo a eliminar con el sucesor
        if successor_parent != node:
            successor_parent.left = successor.right
            successor.right = node.right
        
        successor.left = node.left
        
        return successor
    
    def list_collaborators(self) -> List[Collaborator]:
        """Lista todos los colaboradores ordenados alfabéticamente (preorden)"""
        result = []
        self._list_collaborators_preorder(self.root, result)
        return result
    
    def _list_collaborators_preorder(self, node: Optional[BSTNode], result: List[Collaborator]):
        """Recorrido preorden del árbol de colaboradores"""
        if not node:
            return
        
        # Preorden: raíz, izquierda, derecha
        result.append(node.collaborator)
        self._list_collaborators_preorder(node.left, result)
        self._list_collaborators_preorder(node.right, result)
    
    def to_dict(self) -> Dict:
        """Convierte el árbol a un diccionario para serialización"""
        return {
            "root": self.root.to_dict() if self.root else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CollaboratorsBST':
        """Crea un árbol desde un diccionario"""
        tree = cls()
        if data["root"]:
            tree.root = BSTNode.from_dict(data["root"])
        return tree

# 3. MÓDULO DE GESTIÓN DE ARCHIVOS GIT CON B-TREE
class BTreeNode:
    """Nodo para el B-Tree de archivos Git"""
    def __init__(self, leaf: bool = True, order: int = 5):
        self.leaf = leaf  # Indica si es un nodo hoja
        self.keys = []  # Lista de claves (hashes SHA-1)
        self.values = []  # Lista de valores (archivos)
        self.children = []  # Lista de nodos hijos
        self.order = order  # Orden del B-Tree
    
    def is_full(self) -> bool:
        """Verifica si el nodo está lleno"""
        return len(self.keys) >= self.order - 1
    
    def to_dict(self) -> Dict:
        """Convierte el nodo a un diccionario para serialización"""
        return {
            "leaf": self.leaf,
            "keys": self.keys,
            "values": [value.to_dict() for value in self.values],
            "children": [child.to_dict() for child in self.children],
            "order": self.order
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BTreeNode':
        """Crea un nodo desde un diccionario"""
        node = cls(data["leaf"], data["order"])
        node.keys = data["keys"]
        node.values = [File.from_dict(value) for value in data["values"]]
        
        # Cargar hijos recursivamente
        for child_data in data["children"]:
            node.children.append(cls.from_dict(child_data))
        
        return node

class BTree:
    """B-Tree para gestionar archivos Git"""
    def __init__(self, order: int = 5):
        self.root = BTreeNode(True, order)
        self.order = order
    
    def search(self, key: str, node: Optional[BTreeNode] = None) -> Optional[File]:
        """Busca un archivo por su hash SHA-1"""
        if node is None:
            node = self.root
        
        # Buscar la clave en el nodo actual
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        # Si encontramos la clave
        if i < len(node.keys) and key == node.keys[i]:
            return node.values[i]
        
        # Si es un nodo hoja y no encontramos la clave, no existe
        if node.leaf:
            return None
        
        # Buscar en el hijo correspondiente
        return self.search(key, node.children[i])
    
    def insert(self, file: File):
        """Inserta un archivo en el B-Tree"""
        key = file.checksum
        
        # Si la raíz está llena, dividirla
        if self.root.is_full():
            new_root = BTreeNode(False, self.order)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        
        # Insertar en la raíz
        self._insert_non_full(self.root, key, file)
    
    def _insert_non_full(self, node: BTreeNode, key: str, file: File):
        """Inserta una clave en un nodo no lleno"""
        i = len(node.keys) - 1
        
        # Si es un nodo hoja, insertar directamente
        if node.leaf:
            # Encontrar la posición correcta
            while i >= 0 and key < node.keys[i]:
                i -= 1
            
            # Insertar la clave y el valor
            node.keys.insert(i + 1, key)
            node.values.insert(i + 1, file)
        else:
            # Encontrar el hijo donde insertar
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            # Si el hijo está lleno, dividirlo
            if node.children[i].is_full():
                self._split_child(node, i)
                
                # Después de dividir, la clave media está en el nodo actual
                # Determinar en qué hijo insertar
                if key > node.keys[i]:
                    i += 1
            
            # Insertar en el hijo correspondiente
            self._insert_non_full(node.children[i], key, file)
    
    def _split_child(self, parent: BTreeNode, index: int):
        """Divide un hijo lleno de un nodo"""
        order = self.order
        child = parent.children[index]
        new_child = BTreeNode(child.leaf, order)
        
        # Mover la mitad superior de las claves y valores al nuevo hijo
        mid = order // 2
        parent.keys.insert(index, child.keys[mid])
        parent.values.insert(index, child.values[mid])
        
        new_child.keys = child.keys[mid+1:]
        new_child.values = child.values[mid+1:]
        child.keys = child.keys[:mid]
        child.values = child.values[:mid]
        
        # Si no es un nodo hoja, mover también los hijos
        if not child.leaf:
            new_child.children = child.children[mid+1:]
            child.children = child.children[:mid+1]
        
        # Insertar el nuevo hijo en el padre
        parent.children.insert(index + 1, new_child)
    
    def delete(self, key: str) -> bool:
        """Elimina un archivo del B-Tree por su hash SHA-1"""
        if not self.root.keys:
            return False  # Árbol vacío
        
        result = self._delete_key(self.root, key)
        
        # Si la raíz quedó vacía y no es hoja, hacer que su primer hijo sea la nueva raíz
        if not self.root.keys and not self.root.leaf:
            self.root = self.root.children[0]
        
        return result
    
    def _delete_key(self, node: BTreeNode, key: str) -> bool:
        """Elimina una clave de un nodo o sus descendientes"""
        # Buscar la clave en el nodo actual
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        # Si la clave está en este nodo
        if i < len(node.keys) and key == node.keys[i]:
            if node.leaf:
                # Caso 1: Nodo hoja, simplemente eliminar
                node.keys.pop(i)
                node.values.pop(i)
                return True
            else:
                # Caso 2: Nodo interno
                return self._delete_internal_node(node, i)
        
        # Si la clave no está en este nodo
        if node.leaf:
            return False  # No se encontró la clave
        
        # Verificar si el hijo donde debería estar la clave tiene al menos t claves
        if len(node.children[i].keys) < self.order // 2:
            # Rellenar el hijo si es necesario
            self._fill_child(node, i)
        
        # Si el último hijo se fusionó, buscar en el hijo i-1
        if i > len(node.keys):
            return self._delete_key(node.children[i-1], key)
        else:
            return self._delete_key(node.children[i], key)
    
    def _delete_internal_node(self, node: BTreeNode, idx: int) -> bool:
        """Maneja la eliminación de una clave en un nodo interno"""
        key = node.keys[idx]
        
        # Caso 2a: El hijo anterior a la clave tiene al menos t claves
        if len(node.children[idx].keys) >= self.order // 2:
            # Encontrar el predecesor
            pred = self._get_predecessor(node, idx)
            # Reemplazar la clave con su predecesor
            node.keys[idx] = pred.keys[-1]
            node.values[idx] = pred.values[-1]
            # Eliminar el predecesor recursivamente
            return self._delete_key(node.children[idx], pred.keys[-1])
        
        # Caso 2b: El hijo posterior a la clave tiene al menos t claves
        elif len(node.children[idx+1].keys) >= self.order // 2:
            # Encontrar el sucesor
            succ = self._get_successor(node, idx)
            # Reemplazar la clave con su sucesor
            node.keys[idx] = succ.keys[0]
            node.values[idx] = succ.values[0]
            # Eliminar el sucesor recursivamente
            return self._delete_key(node.children[idx+1], succ.keys[0])
        
        # Caso 2c: Ambos hijos tienen menos de t claves
        else:
            # Fusionar los hijos y la clave
            self._merge_children(node, idx)
            # Eliminar la clave del hijo fusionado
            return self._delete_key(node.children[idx], key)
    
    def _get_predecessor(self, node: BTreeNode, idx: int) -> BTreeNode:
        """Obtiene el nodo que contiene el predecesor de una clave"""
        curr = node.children[idx]
        while not curr.leaf:
            curr = curr.children[-1]
        return curr
    
    def _get_successor(self, node: BTreeNode, idx: int) -> BTreeNode:
        """Obtiene el nodo que contiene el sucesor de una clave"""
        curr = node.children[idx+1]
        while not curr.leaf:
            curr = curr.children[0]
        return curr
    
    def _fill_child(self, node: BTreeNode, idx: int):
        """Asegura que el hijo en el índice idx tenga al menos t claves"""
        # Caso 1: Tomar prestado del hermano izquierdo
        if idx > 0 and len(node.children[idx-1].keys) >= self.order // 2:
            self._borrow_from_prev(node, idx)
        # Caso 2: Tomar prestado del hermano derecho
        elif idx < len(node.children) - 1 and len(node.children[idx+1].keys) >= self.order // 2:
            self._borrow_from_next(node, idx)
        # Caso 3: Fusionar con un hermano
        else:
            if idx < len(node.keys):
                self._merge_children(node, idx)
            else:
                self._merge_children(node, idx-1)
    
    def _borrow_from_prev(self, node: BTreeNode, idx: int):
        """Toma prestada una clave del hijo anterior"""
        child = node.children[idx]
        sibling = node.children[idx-1]
        
        # Mover la clave del nodo al hijo
        child.keys.insert(0, node.keys[idx-1])
        child.values.insert(0, node.values[idx-1])
        
        # Mover la última clave del hermano al nodo
        node.keys[idx-1] = sibling.keys[-1]
        node.values[idx-1] = sibling.values[-1]
        
        # Si no es hoja, mover también el último hijo del hermano
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())
        
        # Eliminar la clave del hermano
        sibling.keys.pop()
        sibling.values.pop()
    
    def _borrow_from_next(self, node: BTreeNode, idx: int):
        """Toma prestada una clave del hijo siguiente"""
        child = node.children[idx]
        sibling = node.children[idx+1]
        
        # Mover la clave del nodo al hijo
        child.keys.append(node.keys[idx])
        child.values.append(node.values[idx])
        
        # Mover la primera clave del hermano al nodo
        node.keys[idx] = sibling.keys[0]
        node.values[idx] = sibling.values[0]
        
        # Si no es hoja, mover también el primer hijo del hermano
        if not child.leaf:
            child.children.append(sibling.children.pop(0))
        
        # Eliminar la clave del hermano
        sibling.keys.pop(0)
        sibling.values.pop(0)
    
    def _merge_children(self, node: BTreeNode, idx: int):
        """Fusiona el hijo en el índice idx con el hijo en el índice idx+1"""
        child = node.children[idx]
        sibling = node.children[idx+1]
        
        # Mover la clave del nodo al hijo
        child.keys.append(node.keys[idx])
        child.values.append(node.values[idx])
        
        # Mover todas las claves y valores del hermano al hijo
        child.keys.extend(sibling.keys)
        child.values.extend(sibling.values)
        
        # Si no es hoja, mover también los hijos del hermano
        if not child.leaf:
            child.children.extend(sibling.children)
        
        # Eliminar la clave del nodo y el hermano
        node.keys.pop(idx)
        node.values.pop(idx)
        node.children.pop(idx+1)
    
    def list_files(self) -> List[File]:
        """Lista todos los archivos en el B-Tree (preorden)"""
        result = []
        self._list_files_preorder(self.root, result)
        return result
    
    def _list_files_preorder(self, node: BTreeNode, result: List[File]):
        """Recorrido preorden del B-Tree"""
        if not node:
            return
        
        # Añadir los archivos de este nodo
        result.extend(node.values)
        
        # Recorrer los hijos
        for child in node.children:
            self._list_files_preorder(child, result)
    
    def to_dict(self) -> Dict:
        """Convierte el B-Tree a un diccionario para serialización"""
        return {
            "root": self.root.to_dict(),
            "order": self.order
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BTree':
        """Crea un B-Tree desde un diccionario"""
        tree = cls(data["order"])
        tree.root = BTreeNode.from_dict(data["root"])
        return tree

# 4. MÓDULO DE GESTIÓN DE ROLES Y PERMISOS CON ÁRBOL AVL
class Permission:
    """Clase que representa un permiso en el sistema Git"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para serialización"""
        return {
            "name": self.name,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Permission':
        """Crea un objeto Permission desde un diccionario"""
        return cls(data["name"], data["description"])

class Role:
    """Clase que representa un rol en el sistema Git"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.permissions = []  # Lista de permisos asignados a este rol
    
    def add_permission(self, permission: Permission):
        """Añade un permiso al rol"""
        if permission.name not in [p.name for p in self.permissions]:
            self.permissions.append(permission)
    
    def remove_permission(self, permission_name: str) -> bool:
        """Elimina un permiso del rol"""
        for i, permission in enumerate(self.permissions):
            if permission.name == permission_name:
                self.permissions.pop(i)
                return True
        return False
    
    def has_permission(self, permission_name: str) -> bool:
        """Verifica si el rol tiene un permiso específico"""
        return permission_name in [p.name for p in self.permissions]
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para serialización"""
        return {
            "name": self.name,
            "description": self.description,
            "permissions": [p.to_dict() for p in self.permissions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Role':
        """Crea un objeto Role desde un diccionario"""
        role = cls(data["name"], data["description"])
        for perm_data in data["permissions"]:
            role.add_permission(Permission.from_dict(perm_data))
        return role

class AVLNode:
    """Nodo para el árbol AVL de roles y permisos"""
    def __init__(self, email: str, role: Role):
        self.email = email
        self.role = role
        self.height = 1
        self.left = None
        self.right = None
    
    def to_dict(self) -> Dict:
        """Convierte el nodo a un diccionario para serialización"""
        result = {
            "email": self.email,
            "role": self.role.to_dict(),
            "height": self.height,
            "left": None,
            "right": None
        }
        
        if self.left:
            result["left"] = self.left.to_dict()
        
        if self.right:
            result["right"] = self.right.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> Optional['AVLNode']:
        """Crea un nodo desde un diccionario"""
        if not data:
            return None
        
        node = cls(data["email"], Role.from_dict(data["role"]))
        node.height = data["height"]
        
        if data["left"]:
            node.left = cls.from_dict(data["left"])
        
        if data["right"]:
            node.right = cls.from_dict(data["right"])
        
        return node

class RolesAVLTree:
    """Árbol AVL para gestionar roles y permisos"""
    def __init__(self):
        self.root = None
    
    def _height(self, node: Optional[AVLNode]) -> int:
        """Obtiene la altura de un nodo"""
        if not node:
            return 0
        return node.height
    
    def _balance_factor(self, node: Optional[AVLNode]) -> int:
        """Calcula el factor de balance de un nodo"""
        if not node:
            return 0
        return self._height(node.left) - self._height(node.right)
    
    def _update_height(self, node: AVLNode):
        """Actualiza la altura de un nodo"""
        node.height = 1 + max(self._height(node.left), self._height(node.right))
    
    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """Rotación simple a la derecha"""
        x = y.left
        T2 = x.right
        
        # Realizar rotación
        x.right = y
        y.left = T2
        
        # Actualizar alturas
        self._update_height(y)
        self._update_height(x)
        
        return x
    
    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """Rotación simple a la izquierda"""
        y = x.right
        T2 = y.left
        
        # Realizar rotación
        y.left = x
        x.right = T2
        
        # Actualizar alturas
        self._update_height(x)
        self._update_height(y)
        
        return y
    
    def add_role(self, email: str, role: Role):
        """Añade un rol a un usuario"""
        self.root = self._add_role_recursive(self.root, email, role)
    
    def _add_role_recursive(self, node: Optional[AVLNode], email: str, role: Role) -> AVLNode:
        """Añade un rol recursivamente"""
        # Inserción estándar en un BST
        if not node:
            return AVLNode(email, role)
        
        if email < node.email:
            node.left = self._add_role_recursive(node.left, email, role)
        elif email > node.email:
            node.right = self._add_role_recursive(node.right, email, role)
        else:
            # El email ya existe, actualizar el rol
            node.role = role
            return node
        
        # Actualizar altura del nodo actual
        self._update_height(node)
        
        # Obtener el factor de balance
        balance = self._balance_factor(node)
        
        # Casos de desbalance
        
        # Caso Izquierda-Izquierda
        if balance > 1 and email < node.left.email:
            return self._rotate_right(node)
        
        # Caso Derecha-Derecha
        if balance < -1 and email > node.right.email:
            return self._rotate_left(node)
        
        # Caso Izquierda-Derecha
        if balance > 1 and email > node.left.email:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        
        # Caso Derecha-Izquierda
        if balance < -1 and email < node.right.email:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        
        return node
    
    def remove_role(self, email: str) -> bool:
        """Elimina un rol de un usuario"""
        if not self.root:
            return False
        
        self.root, removed = self._remove_role_recursive(self.root, email)
        return removed
    
    def _remove_role_recursive(self, node: Optional[AVLNode], email: str) -> Tuple[Optional[AVLNode], bool]:
        """Elimina un rol recursivamente"""
        if not node:
            return None, False
        
        if email < node.email:
            node.left, removed = self._remove_role_recursive(node.left, email)
        elif email > node.email:
            node.right, removed = self._remove_role_recursive(node.right, email)
        else:
            # Nodo encontrado, eliminarlo
            
            # Caso 1: Nodo sin hijos o con un solo hijo
            if not node.left:
                return node.right, True
            elif not node.right:
                return node.left, True
            
            # Caso 2: Nodo con dos hijos
            # Encontrar el sucesor inorden (el menor valor en el subárbol derecho)
            successor = self._find_min_value_node(node.right)
            
            # Copiar los datos del sucesor a este nodo
            node.email = successor.email
            node.role = successor.role
            
            # Eliminar el sucesor
            node.right, _ = self._remove_role_recursive(node.right, successor.email)
            
            removed = True
        
        if not node:
            return node, removed
        
        # Actualizar altura
        self._update_height(node)
        
        # Obtener el factor de balance
        balance = self._balance_factor(node)
        
        # Casos de desbalance
        
        # Caso Izquierda-Izquierda
        if balance > 1 and self._balance_factor(node.left) >= 0:
            return self._rotate_right(node), removed
        
        # Caso Izquierda-Derecha
        if balance > 1 and self._balance_factor(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node), removed
        
        # Caso Derecha-Derecha
        if balance < -1 and self._balance_factor(node.right) <= 0:
            return self._rotate_left(node), removed
        
        # Caso Derecha-Izquierda
        if balance < -1 and self._balance_factor(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node), removed
        
        return node, removed
    
    def _find_min_value_node(self, node: AVLNode) -> AVLNode:
        """Encuentra el nodo con el valor mínimo en un subárbol"""
        current = node
        while current.left:
            current = current.left
        return current
    
    def find_role(self, email: str) -> Optional[Role]:
        """Busca el rol de un usuario por su email"""
        node = self._find_node(self.root, email)
        return node.role if node else None
    
    def _find_node(self, node: Optional[AVLNode], email: str) -> Optional[AVLNode]:
        """Busca un nodo por el email del usuario"""
        if not node:
            return None
        
        if email == node.email:
            return node
        
        if email < node.email:
            return self._find_node(node.left, email)
        else:
            return self._find_node(node.right, email)
    
    def check_permission(self, email: str, permission: str) -> bool:
        """Verifica si un usuario tiene un permiso específico"""
        role = self.find_role(email)
        if not role:
            return False
        
        return role.has_permission(permission)
    
    def list_roles(self) -> List[Tuple[str, Role]]:
        """Lista todos los roles (postorden)"""
        result = []
        self._list_roles_postorder(self.root, result)
        return result
    
    def _list_roles_postorder(self, node: Optional[AVLNode], result: List[Tuple[str, Role]]):
        """Recorrido postorden del árbol AVL"""
        if not node:
            return
        
        # Postorden: izquierda, derecha, raíz
        self._list_roles_postorder(node.left, result)
        self._list_roles_postorder(node.right, result)
        result.append((node.email, node.role))
    
    def to_dict(self) -> Dict:
        """Convierte el árbol AVL a un diccionario para serialización"""
        return {
            "root": self.root.to_dict() if self.root else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RolesAVLTree':
        """Crea un árbol AVL desde un diccionario"""
        tree = cls()
        if data["root"]:
            tree.root = AVLNode.from_dict(data["root"])
        return tree

# Modificar la clase Repository para incluir los nuevos módulos
class Repository:
    """Clase que representa un repositorio Git"""
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.commits = LinkedList()  # Lista enlazada de commits
        self.staging_area = Stack()  # Pila para el área de staging
        self.pull_requests = Queue()  # Cola para pull requests
        self.current_branch = "main"  # Rama actual
        self.files = {}  # Diccionario de archivos en el repositorio
        
        # Nuevos módulos
        self.branch_tree = BranchTree()  # Árbol n-ario de ramas
        self.collaborators_bst = CollaboratorsBST()  # Árbol binario de búsqueda de colaboradores
        self.files_btree = BTree()  # B-Tree de archivos
        self.roles_avl = RolesAVLTree()  # Árbol AVL de roles y permisos
        
        # Inicializar con datos por defecto
        self._init_default_data()
    
    def _init_default_data(self):
        """Inicializa el repositorio con datos por defecto"""
        # Añadir colaborador administrador
        admin_role = Role("admin", "Acceso total a todas las funciones del repositorio")
        admin_role.add_permission(Permission("push", "Puede hacer push a cualquier rama"))
        admin_role.add_permission(Permission("pull", "Puede hacer pull de cualquier rama"))
        admin_role.add_permission(Permission("merge", "Puede hacer merge entre ramas"))
        
        self.roles_avl.add_role("admin@example.com", admin_role)
        
        # Añadir colaborador por defecto
        collaborator = Collaborator("Usuario Predeterminado", "usuario@example.com", "contributor")
        self.collaborators_bst.add_collaborator(collaborator)
    
    def get_branch(self, name: str) -> Optional[BranchNode]:
        """Obtiene una rama por su nombre"""
        return self.branch_tree.find_branch(name)
    
    def get_current_branch(self) -> BranchNode:
        """Obtiene la rama actual"""
        return self.branch_tree.current
    
    def add_file_to_staging(self, file: File):
        """Añade un archivo al área de staging"""
        self.staging_area.push(file)
        # Actualizar o añadir el archivo al repositorio
        self.files[file.name] = file
        # Añadir el archivo al B-Tree
        self.files_btree.insert(file)
    
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
        
        # Añadir el commit a la rama actual
        current_branch.add_commit(commit)
        
        # Incrementar las contribuciones del autor
        self._increment_contributor_contributions(author_email)
        
        return commit
    
    def _increment_contributor_contributions(self, email: str):
        """Incrementa el contador de contribuciones de un colaborador"""
        # Buscar el colaborador por su email
        collaborators = self.collaborators_bst.list_collaborators()
        for collaborator in collaborators:
            if collaborator.email == email:
                collaborator.add_contribution()
                break
    
    def checkout_branch(self, branch_name: str) -> bool:
        """Cambia a una rama específica (inorden)"""
        result = self.branch_tree.checkout_branch(branch_name)
        if result:
            self.current_branch = branch_name
        return result
    
    def create_branch(self, branch_name: str) -> bool:
        """Crea una nueva rama"""
        return self.branch_tree.create_branch(branch_name)
    
    def delete_branch(self, branch_name: str) -> bool:
        """Elimina una rama si ya ha sido fusionada"""
        return self.branch_tree.delete_branch(branch_name)
    
    def list_branches(self) -> List[str]:
        """Lista todas las ramas en formato jerárquico (preorden)"""
        return self.branch_tree.list_branches()
    
    def merge_branches(self, source_name: str, target_name: str) -> bool:
        """Fusiona una rama en otra (postorden)"""
        return self.branch_tree.merge_branches(source_name, target_name)
    
    def add_collaborator(self, name: str, email: str, role: str = "contributor") -> bool:
        """Añade un colaborador al repositorio"""
        collaborator = Collaborator(name, email, role)
        self.collaborators_bst.add_collaborator(collaborator)
        return True
    
    def remove_collaborator(self, name: str) -> bool:
        """Elimina un colaborador del repositorio"""
        return self.collaborators_bst.remove_collaborator(name)
    
    def find_collaborator(self, name: str) -> Optional[Collaborator]:
        """Busca un colaborador por su nombre (inorden)"""
        return self.collaborators_bst.find_collaborator(name)
    
    def list_collaborators(self) -> List[Collaborator]:
        """Lista todos los colaboradores ordenados alfabéticamente (preorden)"""
        return self.collaborators_bst.list_collaborators()
    
    def add_role(self, email: str, role_name: str, permissions: List[str]) -> bool:
        """Añade un rol a un usuario"""
        # Verificar si el usuario que ejecuta el comando es administrador
        if not self.roles_avl.check_permission("admin@example.com", "merge"):
            print("Solo el administrador puede gestionar roles y permisos.")
            return False
        
        # Crear el rol
        role = Role(role_name, f"Rol {role_name}")
        
        # Añadir permisos
        for perm_name in permissions:
            role.add_permission(Permission(perm_name, f"Permiso para {perm_name}"))
        
        # Añadir el rol al usuario
        self.roles_avl.add_role(email, role)
        return True
    
    def update_role(self, email: str, role_name: str, permissions: List[str]) -> bool:
        """Actualiza el rol de un usuario"""
        # Verificar si el usuario que ejecuta el comando es administrador
        if not self.roles_avl.check_permission("admin@example.com", "merge"):
            print("Solo el administrador puede gestionar roles y permisos.")
            return False
        
        # Eliminar el rol actual
        self.roles_avl.remove_role(email)
        
        # Crear y añadir el nuevo rol
        return self.add_role(email, role_name, permissions)
    
    def remove_role(self, email: str) -> bool:
        """Elimina el rol de un usuario"""
        # Verificar si el usuario que ejecuta el comando es administrador
        if not self.roles_avl.check_permission("admin@example.com", "merge"):
            print("Solo el administrador puede gestionar roles y permisos.")
            return False
        
        return self.roles_avl.remove_role(email)
    
    def show_role(self, email: str) -> Optional[Role]:
        """Muestra el rol y permisos de un usuario"""
        return self.roles_avl.find_role(email)
    
    def check_permission(self, email: str, action: str) -> bool:
        """Verifica si un usuario tiene permiso para realizar una acción"""
        return self.roles_avl.check_permission(email, action)
    
    def list_roles(self) -> List[Tuple[str, Role]]:
        """Lista todos los roles y permisos (postorden)"""
        return self.roles_avl.list_roles()
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para serialización"""
        return {
            "name": self.name,
            "path": self.path,
            "commits": [commit.to_dict() for commit in self.commits.to_list()],
            "current_branch": self.current_branch,
            "files": {name: file.to_dict() for name, file in self.files.items()},
            "pull_requests": [pr.to_dict() for pr in self.pull_requests.to_list()],
            "branch_tree": self.branch_tree.to_dict(),
            "collaborators_bst": self.collaborators_bst.to_dict(),
            "files_btree": self.files_btree.to_dict(),
            "roles_avl": self.roles_avl.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Repository':
        """Crea un objeto Repository desde un diccionario"""
        repo = cls(data["name"], data["path"])
        
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
        
        # Cargar árbol de ramas
        if "branch_tree" in data:
            repo.branch_tree = BranchTree.from_dict(data["branch_tree"])
        
        # Cargar árbol de colaboradores
        if "collaborators_bst" in data:
            repo.collaborators_bst = CollaboratorsBST.from_dict(data["collaborators_bst"])
        
        # Cargar B-Tree de archivos
        if "files_btree" in data:
            repo.files_btree = BTree.from_dict(data["files_btree"])
        
        # Cargar árbol AVL de roles
        if "roles_avl" in data:
            repo.roles_avl = RolesAVLTree.from_dict(data["roles_avl"])
        
        return repo

# Modificar la clase GitSystem para incluir los nuevos comandos
class GitSystem:
    """Clase principal que gestiona el sistema Git"""
    def __init__(self):
        self.repositories = LinkedList()
        self.current_repository = None
        self.user_email = "usuario@example.com"  # Email por defecto
        
        # Asegurar que existe el directorio de datos
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        # Cargar datos si existen
        self._load_data()
    
    def _get_repo_file_path(self, repo_name: str) -> str:
        """Obtiene la ruta del archivo JSON para un repositorio"""
        return os.path.join(DATA_DIR, f"{repo_name}.json")
    
    def _load_data(self):
        """Carga los datos del sistema desde archivos JSON"""
        # Cargar índice de repositorios
        if os.path.exists(REPOS_FILE):
            try:
                with open(REPOS_FILE, 'r') as f:
                    repos_index = json.load(f)
                    
                    # Cargar cada repositorio
                    for repo_name in repos_index:
                        repo_file = self._get_repo_file_path(repo_name)
                        if os.path.exists(repo_file):
                            with open(repo_file, 'r') as repo_f:
                                repo_data = json.load(repo_f)
                                self.repositories.append(Repository.from_dict(repo_data))
            except Exception as e:
                print(f"Error al cargar los datos: {e}")
        else:
            # Crear un índice vacío
            with open(REPOS_FILE, 'w') as f:
                json.dump([], f)
    
    def _save_data(self):
        """Guarda los datos del sistema en archivos JSON"""
        # Guardar índice de repositorios
        repos_names = [repo.name for repo in self.repositories.to_list()]
        with open(REPOS_FILE, 'w') as f:
            json.dump(repos_names, f, indent=2)
        
        # Guardar cada repositorio en su propio archivo
        for repo in self.repositories.to_list():
            repo_file = self._get_repo_file_path(repo.name)
            with open(repo_file, 'w') as f:
                json.dump(repo.to_dict(), f, indent=2)
    
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
            # Subcomandos de branch
            if not args:
                # Listar ramas
                return self._git_branch_list()
            elif args[0] == "-d" and len(args) > 1:
                # Eliminar rama
                return self._git_branch_delete(args[1])
            elif args[0] == "--list":
                # Listar ramas en formato jerárquico
                return self._git_branch_list()
            else:
                # Crear rama
                return self._git_branch_create(args[0])
        elif command == "merge":
            if len(args) < 2:
                print("Uso: git merge <rama_origen> <rama_destino>")
                return None
            return self._git_merge(args[0], args[1])
        elif command == "contributors":
            # Listar colaboradores
            return self._git_contributors()
        elif command == "add-contributor":
            if len(args) < 1:
                print("Uso: git add-contributor <nombre>")
                return None
            return self._git_add_contributor(args[0])
        elif command == "remove-contributor":
            if len(args) < 1:
                print("Uso: git remove-contributor <nombre>")
                return None
            return self._git_remove_contributor(args[0])
        elif command == "find-contributor":
            if len(args) < 1:
                print("Uso: git find-contributor <nombre>")
                return None
            return self._git_find_contributor(args[0])
        elif command == "role":
            if len(args) < 1:
                print("Uso: git role <subcomando> [argumentos]")
                return None
            
            subcommand = args[0]
            if subcommand == "add" and len(args) >= 4:
                # Añadir rol
                email = args[1]
                role = args[2]
                permissions = args[3].split(",")
                return self._git_role_add(email, role, permissions)
            elif subcommand == "update" and len(args) >= 4:
                # Actualizar rol
                email = args[1]
                role = args[2]
                permissions = args[3].split(",")
                return self._git_role_update(email, role, permissions)
            elif subcommand == "remove" and len(args) >= 2:
                # Eliminar rol
                email = args[1]
                return self._git_role_remove(email)
            elif subcommand == "show" and len(args) >= 2:
                # Mostrar rol
                email = args[1]
                return self._git_role_show(email)
            elif subcommand == "check" and len(args) >= 3:
                # Verificar permiso
                email = args[1]
                action = args[2]
                return self._git_role_check(email, action)
            elif subcommand == "list":
                # Listar roles
                return self._git_role_list()
            else:
                print(f"Subcomando de role desconocido o argumentos insuficientes: {subcommand}")
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
        
        status = {
            "branch": repo.current_branch,
            "staged_files": [file.name for file in staged_files],
            "modified_files": [name for name, file in repo.files.items() 
                              if file.status == "M" and file not in staged_files],
            "untracked_files": [name for name, file in repo.files.items() 
                               if file.status == "A" and file not in staged_files]
        }
        
        # Mostrar información de forma simplificada
        print(f"En rama: {status['branch']}")
        
        if staged_files:
            print("\nCambios a confirmar:")
            for file in staged_files:
                print(f"  {file.name} ({file.status})")
        
        modified = status["modified_files"]
        if modified:
            print("\nCambios no preparados para commit:")
            for file in modified:
                print(f"  {file}")
        
        untracked = status["untracked_files"]
        if untracked:
            print("\nArchivos sin seguimiento:")
            for file in untracked:
                print(f"  {file}")
        
        if not staged_files and not modified and not untracked:
            print("Directorio de trabajo limpio")
        
        return status
    
    def _git_log(self) -> List[Dict]:
        """Implementa el comando git log"""
        commits = self.current_repository.commits.to_list()
        
        if not commits:
            print("No hay commits en este repositorio.")
            return []
        
        # Mostrar información de forma simplificada
        print("Historial de commits:")
        for commit in commits:
            print(f"Commit: {commit.id}")
            print(f"Autor: {commit.author_email}")
            print(f"Fecha: {commit.timestamp.split('T')[0]}")
            print(f"Mensaje: {commit.message}")
            if commit.parent_id:
                print(f"Padre: {commit.parent_id}")
            print("-" * 40)
        
        return [commit.to_dict() for commit in commits]
    
    def _git_add(self, file_path: str) -> bool:
        """Implementa el comando git add"""
        repo = self.current_repository
        
        # Verificar si el usuario tiene permiso para añadir archivos
        if not repo.check_permission(self.user_email, "push"):
            print(f"El usuario {self.user_email} no tiene permiso para añadir archivos.")
            return False
        
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
        
        print(f"Archivo '{file_path}' añadido al área de staging.")
        return True
    
    def _git_commit(self, message: str) -> Optional[Dict]:
        """Implementa el comando git commit"""
        repo = self.current_repository
        
        # Verificar si el usuario tiene permiso para hacer commit
        if not repo.check_permission(self.user_email, "push"):
            print(f"El usuario {self.user_email} no tiene permiso para hacer commit.")
            return None
        
        # Crear el commit
        commit = repo.create_commit(message, self.user_email)
        if not commit:
            return None
        
        # Guardar los datos
        self._save_data()
        
        print(f"Commit creado: {commit.id}")
        print(f"Mensaje: {commit.message}")
        
        return commit.to_dict()
    
    def _git_checkout(self, target: str) -> bool:
        """Implementa el comando git checkout (inorden)"""
        repo = self.current_repository
        
        # Verificar si el usuario tiene permiso para cambiar de rama
        if not repo.check_permission(self.user_email, "pull"):
            print(f"El usuario {self.user_email} no tiene permiso para cambiar de rama.")
            return False
        
        # Verificar si es una rama
        result = repo.checkout_branch(target)
        if result:
            print(f"Cambiado a la rama '{target}'")
            # Guardar los datos
            self._save_data()
            return True
        
        # Si no es una rama, intentar como commit
        commit = repo.get_commit_by_id(target)
        if commit:
            # Crear una rama temporal para el commit
            temp_branch_name = f"temp-{target[:6]}"
            repo.create_branch(temp_branch_name)
            
            # Cambiar a la rama temporal
            result = repo.checkout_branch(temp_branch_name)
            if result:
                print(f"HEAD está ahora en el commit {target}")
                # Guardar los datos
                self._save_data()
                return True
        
        print(f"No se encontró la rama o commit '{target}'")
        return False
    
    def _git_branch_create(self, branch_name: str) -> bool:
        """Implementa el comando git branch <nombre_rama>"""
        repo = self.current_repository
        
        # Verificar si el usuario tiene permiso para crear ramas
        if not repo.check_permission(self.user_email, "push"):
            print(f"El usuario {self.user_email} no tiene permiso para crear ramas.")
            return False
        
        result = repo.create_branch(branch_name)
        
        # Guardar los datos
        if result:
            self._save_data()
            print(f"Rama '{branch_name}' creada.")
        
        return result
    
    def _git_branch_delete(self, branch_name: str) -> bool:
        """Implementa el comando git branch -d <nombre_rama>"""
        repo = self.current_repository
        
        # Verificar si el usuario tiene permiso para eliminar ramas
        if not repo.check_permission(self.user_email, "push"):
            print(f"El usuario {self.user_email} no tiene permiso para eliminar ramas.")
            return False
        
        result = repo.delete_branch(branch_name)
        
        # Guardar los datos
        if result:
            self._save_data()
            print(f"Rama '{branch_name}' eliminada.")
        
        return result
    
    def _git_branch_list(self) -> List[str]:
        """Implementa el comando git branch --list"""
        repo = self.current_repository
        branches = repo.list_branches()
        
        if not branches:
            print("No hay ramas en este repositorio.")
            return []
        
        # Mostrar información de forma simplificada
        print("Ramas del repositorio:")
        for branch in branches:
            print(branch)
        
        return branches
    
    def _git_merge(self, source_branch: str, target_branch: str) -> bool:
        """Implementa el comando git merge <rama_origen> <rama_destino>"""
        repo = self.current_repository
        
        # Verificar si el usuario tiene permiso para hacer merge
        if not repo.check_permission(self.user_email, "merge"):
            print(f"El usuario {self.user_email} no tiene permiso para hacer merge.")
            return False
        
        result = repo.merge_branches(source_branch, target_branch)
        
        # Guardar los datos
        if result:
            self._save_data()
            print(f"Rama '{source_branch}' fusionada en '{target_branch}'.")
        
        return result
    
    def _git_contributors(self) -> List[Dict]:
        """Implementa el comando git contributors"""
        repo = self.current_repository
        collaborators = repo.list_collaborators()
        
        if not collaborators:
            print("No hay colaboradores en este repositorio.")
            return []
        
        # Mostrar información de forma simplificada
        print("Colaboradores del repositorio:")
        for collaborator in collaborators:
            print(f"Nombre: {collaborator.name}")
            print(f"Email: {collaborator.email}")
            print(f"Rol: {collaborator.role}")
            print(f"Contribuciones: {collaborator.contributions}")
            print("-" * 30)
        
        return [{"name": c.name, "email": c.email, "role": c.role} for c in collaborators]
    
    def _git_add_contributor(self, name: str) -> bool:
        """Implementa el comando git add-contributor <nombre>"""
        repo = self.current_repository
        
        # Solicitar email y rol
        email = input("Email del colaborador: ")
        role = input("Rol del colaborador (contributor, maintainer, admin): ")
        
        # Verificar si el usuario tiene permiso para añadir colaboradores
        if not repo.check_permission(self.user_email, "merge"):
            print(f"El usuario {self.user_email} no tiene permiso para añadir colaboradores.")
            return False
        
        result = repo.add_collaborator(name, email, role)
        
        # Guardar los datos
        if result:
            self._save_data()
            print(f"Colaborador '{name}' añadido.")
        
        return result
    
    def _git_remove_contributor(self, name: str) -> bool:
        """Implementa el comando git remove-contributor <nombre>"""
        repo = self.current_repository
        
        # Verificar si el usuario tiene permiso para eliminar colaboradores
        if not repo.check_permission(self.user_email, "merge"):
            print(f"El usuario {self.user_email} no tiene permiso para eliminar colaboradores.")
            return False
        
        result = repo.remove_collaborator(name)
        
        # Guardar los datos
        if result:
            self._save_data()
            print(f"Colaborador '{name}' eliminado.")
        
        return result
    
    def _git_find_contributor(self, name: str) -> Optional[Dict]:
        """Implementa el comando git find-contributor <nombre>"""
        repo = self.current_repository
        collaborator = repo.find_collaborator(name)
        
        if not collaborator:
            print(f"No se encontró el colaborador '{name}'.")
            return None
        
        # Mostrar información de forma simplificada
        print(f"Colaborador encontrado:")
        print(f"Nombre: {collaborator.name}")
        print(f"Email: {collaborator.email}")
        print(f"Rol: {collaborator.role}")
        print(f"Contribuciones: {collaborator.contributions}")
        
        return collaborator.to_dict()
    
    def _git_role_add(self, email: str, role_name: str, permissions: List[str]) -> bool:
        """Implementa el comando git role add <email> <role> <permissions>"""
        repo = self.current_repository
        
        result = repo.add_role(email, role_name, permissions)
        
        # Guardar los datos
        if result:
            self._save_data()
            print(f"Rol '{role_name}' con permisos {permissions} añadido a '{email}'.")
        
        return result
    
    def _git_role_update(self, email: str, role_name: str, permissions: List[str]) -> bool:
        """Implementa el comando git role update <email> <new_role> <new_permissions>"""
        repo = self.current_repository
        
        result = repo.update_role(email, role_name, permissions)
        
        # Guardar los datos
        if result:
            self._save_data()
            print(f"Rol de '{email}' actualizado a '{role_name}' con permisos {permissions}.")
        
        return result
    
    def _git_role_remove(self, email: str) -> bool:
        """Implementa el comando git role remove <email>"""
        repo = self.current_repository
        
        result = repo.remove_role(email)
        
        # Guardar los datos
        if result:
            self._save_data()
            print(f"Rol de '{email}' eliminado.")
        
        return result
    
    def _git_role_show(self, email: str) -> Optional[Dict]:
        """Implementa el comando git role show <email>"""
        repo = self.current_repository
        role = repo.show_role(email)
        
        if not role:
            print(f"No se encontró un rol para '{email}'.")
            return None
        
        # Mostrar información de forma simplificada
        print(f"Rol de '{email}':")
        print(f"Nombre: {role.name}")
        print(f"Descripción: {role.description}")
        print("Permisos:")
        for perm in role.permissions:
            print(f"  - {perm.name}: {perm.description}")
        
        return role.to_dict()
    
    def _git_role_check(self, email: str, action: str) -> bool:
        """Implementa el comando git role check <email> <action>"""
        repo = self.current_repository
        result = repo.check_permission(email, action)
        
        if result:
            print(f"'{email}' tiene permiso para '{action}'.")
        else:
            print(f"'{email}' NO tiene permiso para '{action}'.")
        
        return result
    
    def _git_role_list(self) -> List[Dict]:
        """Implementa el comando git role list"""
        repo = self.current_repository
        roles = repo.list_roles()
        
        if not roles:
            print("No hay roles definidos en este repositorio.")
            return []
        
        # Mostrar información de forma simplificada
        print("Roles del repositorio:")
        for email, role in roles:
            print(f"Email: {email}")
            print(f"Rol: {role.name}")
            print("Permisos:")
            for perm in role.permissions:
                print(f"  - {perm.name}")
            print("-" * 30)
        
        return [{"email": email, "role": role.name} for email, role in roles]

def main():
    """Función principal del programa"""
    git_system = GitSystem()
    
    # Cargar datos de prueba si no hay repositorios
    if git_system.repositories.is_empty():
        _load_test_data(git_system)
    
    print("Inicie la sesion con el usuario admin@example.com haciendo uso del 'git use <email>'\nSistema de Simulación Git")
    print("=========================")
    
    while True:
        # Mostrar el repositorio actual
        if git_system.current_repository:
            prompt = f"\n[{git_system.current_repository.name}] git> "
        else:
            prompt = "\ngit> "
        
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
        elif command == "help":
            # Mostrar ayuda
            _show_help()
            continue
        
        # Ejecutar comando Git
        try:
            git_system.execute_command(command, args)
        except Exception as e:
            print(f"Error: {e}")

def _show_help():
    """Muestra la ayuda del programa"""
    print("\nAyuda del Sistema de Simulación Git")
    print("==================================")
    print("\nComandos del sistema:")
    print("  repos                  - Lista los repositorios disponibles")
    print("  use <repo>             - Selecciona un repositorio")
    print("  email [nuevo_email]    - Muestra o establece el email del usuario")
    print("  help                   - Muestra esta ayuda")
    print("  exit, quit, q          - Sale del programa")
    
    print("\nComandos Git:")
    print("  git init <nombre>      - Crea un nuevo repositorio")
    print("  git status             - Muestra el estado del repositorio")
    print("  git log                - Muestra el historial de commits")
    print("  git add <archivo>      - Añade un archivo al área de staging")
    print("  git commit -m \"msg\"    - Crea un nuevo commit con los archivos en staging")
    
    print("\nComandos de Gestión de Branches (Árbol N-ario):")
    print("  git branch <nombre>    - Crea una nueva rama bajo la rama actual")
    print("  git branch -d <nombre> - Elimina una rama si ya ha sido fusionada")
    print("  git branch --list      - Muestra todas las ramas en formato jerárquico (preorden)")
    print("  git checkout <nombre>  - Cambia a una rama específica (inorden)")
    print("  git merge <origen> <destino> - Fusiona una rama en otra (postorden)")
    
    print("\nComandos de Administración de Colaboradores (Árbol Binario de Búsqueda):")
    print("  git contributors       - Muestra la lista de colaboradores ordenada alfabéticamente (preorden)")
    print("  git add-contributor <nombre> - Agrega un nuevo colaborador en la estructura")
    print("  git remove-contributor <nombre> - Elimina un colaborador y reorganiza el árbol")
    print("  git find-contributor <nombre> - Busca un colaborador por su nombre (inorden)")
    
    print("\nComandos de Gestión de Roles y Permisos (Árbol AVL):")
    print("  git role add <email> <role> <permisos> - Agrega un nuevo colaborador con rol y permisos")
    print("  git role update <email> <role> <permisos> - Actualiza rol de un colaborador")
    print("  git role remove <email> - Elimina un rol a un colaborador según su email")
    print("  git role show <email> - Ver los permisos y el rol asignado a un usuario")
    print("  git role check <email> <action> - Verificar si un usuario tiene permiso para una acción")
    print("  git role list - Listar todos los colaboradores con sus roles y permisos (postorden)")

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
    
    # Añadir colaboradores
    repo.add_collaborator("Juan Pérez", "juan@example.com", "developer")
    repo.add_collaborator("María García", "maria@example.com", "maintainer")
    repo.add_collaborator("Carlos López", "carlos@example.com", "admin")
    
    # Configurar roles y permisos
    admin_role = Role("admin", "Acceso total a todas las funciones del repositorio")
    admin_role.add_permission(Permission("push", "Puede hacer push en cualquier rama"))
    admin_role.add_permission(Permission("pull", "Puede hacer pull de cualquier rama"))
    admin_role.add_permission(Permission("merge", "Puede hacer merge entre ramas"))
    
    maintainer_role = Role("maintainer", "Puede hacer push y merge en cualquier rama")
    maintainer_role.add_permission(Permission("push", "Puede hacer push en cualquier rama"))
    maintainer_role.add_permission(Permission("pull", "Puede hacer pull de cualquier rama"))
    maintainer_role.add_permission(Permission("merge", "Puede hacer merge entre ramas"))
    
    developer_role = Role("developer", "Acceso para hacer push en ramas específicas")
    developer_role.add_permission(Permission("push", "Puede hacer push en ramas específicas"))
    developer_role.add_permission(Permission("pull", "Puede hacer pull de cualquier rama"))
    
    repo.roles_avl.add_role("carlos@example.com", admin_role)
    repo.roles_avl.add_role("maria@example.com", maintainer_role)
    repo.roles_avl.add_role("juan@example.com", developer_role)
    
    # Volver a la rama principal
    git_system.execute_command("checkout", ["main"])
    
    print("Datos de prueba cargados correctamente.")

if __name__ == "__main__":
    main()