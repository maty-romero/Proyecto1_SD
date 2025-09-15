
class Nodo: # La logica esta sin implementar, hay que revisar
    def __init__(self, id):
        self.id = id
        self.estado = {}

    def get_id_nodo(self):
        return self.id

    def set_id_nodo(self, id):
        self.id = id

    def obtener_estado(self):
        return self.estado

    def actualizar_estado(self, datos):
        self.estado.update(datos)

    # Evaluar si esto queda aca
    # def iniciar_daemon(self):
    #     # Inicia el daemon Pyro
    #     pass

    # def registrar_en_nameserver(self, nombre):
    #     # Registra el objeto en el Name Server
    #     pass

    def mostrar_estado(self):
        print(f"Estado del nodo {self.id}: {self.estado}")