from Main.Server.Nodo import Nodo


class Replica(Nodo):
    def __init__(self, id, servidor_ref):
        super().__init__(id)
        self.servidor_ref = servidor_ref
        self.es_primaria = False

    def sincronizar_con_servidor(self):
        estado = self.servidor_ref.obtener_estado()
        self.actualizar_estado(estado)

    def enviar_heartbeat(self):
        # Notifica al servidor que sigue activa
        pass

    def asumir_rol_primario(self):
        self.es_primaria = True
        # Cambia comportamiento si es necesario
        pass