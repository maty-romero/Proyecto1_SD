
class Nodo: # La logica esta sin implementar, hay que revisar
    def __init__(self, id, nombre, activo):
        self.id = id
        self.nombre = nombre
        self.activo = activo #por lo pronto dos estados, o es nodo activo, o no lo es (es replica)
        #si se complejiza funcionalidad, self.estado="activo"-->"inactivo"-->"sincronizando"

    def get_id_nodo(self):
        return self.id

    def get_nombre_completo(self):
        return f"{self.nombre}-{self.id}"
    
    def set_id_nodo(self, id):
        self.id = id

    def obtener_estado(self):
        return self.estado

    def actualizar_estado(self, datos):
        self.estado.update(datos)


    def mostrar_estado(self):
        print(f"Estado del nodo {self.id}: {self.estado}")