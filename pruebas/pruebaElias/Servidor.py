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

    def verificar_nameserver(self):
        """Verifica si el servidor de nombres esta disponible"""
        try:
            Pyro5.api.locate_ns()
            return True
        except (errors.NamingError, errors.CommunicationError, ConnectionRefusedError) as e:
            print(f"No se pudo conectar al servidor de nombres: {e}")
            return False

    def iniciar_nameserver(self):
        """Intenta iniciar el nameserver si no está disponible"""
        if self.verificar_nameserver():
            print("El servidor de nombres ya está ejecutándose")
            return True
        print("Iniciando el servidor de Nombres...")
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "Pyro5.nameserver"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            time.sleep(3)
            return self.verificar_nameserver()
        except Exception as e:
            print(f" Error al iniciar el servidor de nombres: {e}")
            return False
    
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