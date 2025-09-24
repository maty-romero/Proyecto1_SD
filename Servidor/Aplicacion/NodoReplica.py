"""
-Falta implementar hilo de escucha
-Falta implementar metodo que calcule el timeout del servidor

"""


#implementa patron de failover
class ReplicaServidor(NodoServidor):
    def __init__(self, id, nombre="Replica", active=False):
        super().__init__(id,nombre,active)
        #nodo replica tambien tiene una instancia propia de DB

    #se invoca este metodo cuando no se detecto 
    def check_failover(self, main_server):
        if not main_server.active:
            self.logger.warning(f"Se detecto fallo en el servidor. Cambiando {self.get_nombre_completo()} a nodo principal")
            self.active = True
            self.nombre = "Servidor"
            self.iniciar_servicio()
            self.logger.warning(f"El nuevo nombre de la replica es {self.get_nombre_completo()} ")
            # aquí conectarse o sincronizar con el NameServer
    
    #puede servir para impresiones en logger, o como registro
    # def actualizar_estado(self, datos):
    #     self.estado.update(datos)
    #     self.logger.info(f"Réplica {self.id} actualizada con datos: {datos}")