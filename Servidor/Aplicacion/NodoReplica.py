"""
-Falta implementar hilo de escucha
-Falta implementar metodo que calcule el timeout del servidor

"""
from Servidor.Aplicacion.ManejadorSocketReplica import ManejadorSocketReplica
from Servidor.Aplicacion.ManejadorSocketServidor import ManejadorSocketServidor
from Servidor.Aplicacion.NodoServidor import NodoServidor
from Servidor.Persistencia.ControladorDB import ControladorDB
from Servidor.Utils.ConsoleLogger import ConsoleLogger


#implementa patron de failover
class NodoReplica(NodoServidor):
    def __init__(self, id, host, puerto, coordinador_id: int, nombre="Replica", activo=False):
        super().__init__(id, host=host, puerto=puerto, nombre=nombre, activo=activo)
        self.ServDB = ControladorDB()
        # self.ControladorDB() --> PENDIENTE
        self.id_coordinador_actual = coordinador_id
        self.socket_manager = None
        self.logger = ConsoleLogger(name=f"NodoReplica[{self.get_nombre_completo()}]", level="INFO") # Sobrescritura

    def iniciar_replica(self):
        self.logger.info(f"{self.get_nombre_completo()} conectándose a nodo primario {self.id_coordinador_actual}")

        #self.logger.error(self.nodos_cluster)
        coincidencias = [n for n in self.nodos_cluster if n.id == self.id_coordinador_actual]
        coord = coincidencias[0] if coincidencias else None
        #self.logger.error(coord)

        self.socket_manager = ManejadorSocketReplica(
            coord.host,
            coord.puerto,
            self._on_msg,
            self.get_nombre_completo())
        self.socket_manager.conectar()

    def _on_msg(self, mensaje):
        self.logger.info(f"Mensaje recibido del primario: {mensaje}")
        # Aquí procesás heartbeats, updates, etc.

    def promover_a_principal(self):
        self.logger.warning(f"{self.get_nombre_completo()} promovido a PRIMARIO")
        self.socket_manager.cerrar()
        # Para que pueda enviar heartbeat a N nodos replicas
        self.socket_mgr = ManejadorSocketServidor(self.host, self.puerto, self._on_msg)
        self.id_coordinador_actual = self.id_coordinador_actual
        self.socket_manager.iniciar()

    #se invoca este metodo cuando no se detecto 
    def check_failover(self, main_server):
        if not main_server.active:
            self.logger.warning(f"Se detecto fallo en el servidor. Cambiando {self.get_nombre_completo()} a nodo principal")
            self.active = True
            self.nombre = "Servidor"
            self.iniciar_servicio()
            self.logger.warning(f"El nuevo nombre de la replica es {self.get_nombre_completo()} ")
            # aquí conectarse o sincronizar con el NameServer


    """
    def check_failover(self, main_alive: bool):
        if not main_alive:
            self.logger.warning(f"Fallo detectado. Promoviendo {self.get_nombre_completo()} a PRIMARIO")
            # Aquí podrías instanciar un NodoServidor con los mismos datos
            nuevo = NodoServidor(self.id, self.host, self.port)
            return nuevo
        return self
    """

    #puede servir para impresiones en logger, o como registro
    # def actualizar_estado(self, datos):
    #     self.estado.update(datos)
    #     self.logger.info(f"Réplica {self.id} actualizada con datos: {datos}")

    """
    Otra definicion de NodoReplica que habia
    
    class NodoReplica(Nodo):
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
    """