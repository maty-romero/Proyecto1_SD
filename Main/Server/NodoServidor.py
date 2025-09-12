from Main.Server.Nodo import Nodo
from Main.Server import ConexionServidor
from Main.Server import GestorPartida

class Servidor(Nodo):
    def __init__(self, id, Conexion = ConexionServidor(),Gestor= GestorPartida()):
        super().__init__(id, Conexion)    
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