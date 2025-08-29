import Pyro5.api
import subprocess #consultar que tan factible es, puede tambien crearse un .bat
import time
import sys
from Nodo import Nodo
from Pyro5 import errors
from builtins import ConnectionRefusedError

class Servidor(Nodo):
    def __init__(self, id):
        super().__init__(id)
        self.replicas = [] # un servidor posee varias replicas
    
    def registrar_replica(self, replica):
        self.replicas.append(replica)
        print(f"Replica {replica.id} registrada")

    def propagar_actualizacion(self, datos):
        self.actualizar_estado(datos)
        for replica in self.replicas:
            replica.actualizar_estado(datos)

    def consultar_bd(self, query):
        # Ejecuta una consulta en la base de datos
        pass

    def guardar_estado_en_bd(self):
        # Persiste el estado actual
        pass