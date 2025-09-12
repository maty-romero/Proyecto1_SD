
#La logica esta sin implementar, hay que revisar
from Main.Common.ConexionBase import ConexionBase

class Nodo:

    def __init__(self, id, conexion: ConexionBase):
        self.id = id
        self.estado = {}
        self.conexion = conexion

    def get_id_nodo(self):
        return self.id

    def set_id_nodo(self,id):
        self.id=id

    def obtener_estado(self):
        return self.estado

    #Puede crearse otro enum para hacer los estados del nodo
    def actualizar_estado(self, datos):
        self.estado.update(datos)

    def mostrar_estado(self):
        print(f"Estado del nodo {self.id}: {self.estado}")