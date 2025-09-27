
class Nodo: # La logica esta sin implementar, hay que revisar
    def __init__(self, id, nombre, host, puerto, activo):
        self.id = id
        self.host = host # uso de ip en pruebas
        self.puerto = puerto # uso de ip en pruebas
        self.nombre = nombre
        self.activo = activo #por lo pronto dos estados, o es nodo activo, o no lo es (es replica)
        #si se complejiza funcionalidad, self.estado="activo"-->"inactivo"-->"sincronizando"
        self.nodos_cluster = []
        self.id_coordinador_actual = None #Id del primario actual
        # self.estado = enum ??

    def registrar_nodo_en_cluster(self, nodo):
        self.nodos_cluster.append(nodo)

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

    # Evaluar si esto queda aca
    # def iniciar_daemon(self):
    #     # Inicia el daemon Pyro
    #     pass

    # def registrar_en_nameserver(self, nombre):
    #     # Registra el objeto en el Name Server
    #     pass
