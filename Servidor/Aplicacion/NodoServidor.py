from Servidor.Aplicacion.Nodo import Nodo
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Comunicacion.ServicioComunicacion import ServicioComunicacion
from Servidor.Dominio.ServicioJuego import ServicioJuego
from Servidor.Persistencia.ControladorDB import ControladorDB
from Servidor.Utils.ConsoleLogger import ConsoleLogger
"""-Falta implementar logica que considere que si el servidor una vez caido, vuelve a funcionar, pase a estado INACTIVO"""
class NodoServidor(Nodo):
    def __init__(self, id, nombre="Servidor", activo=False):
        super().__init__(id,nombre,activo)
        self.logger = ConsoleLogger(name="LoggerLocal", level="INFO")
        self.ServDB = None
        #self.ServDB = ControladorDB(self.logger)
        #analizar posibles modificaciones a esta invocacion
        if self.activo:
            self.iniciar_servicio()

    def iniciar_servicio(self):
        self.ServComunic = ServicioComunicacion()
        self.Dispatcher = Dispatcher()
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComunic)
        self.Dispatcher.registrar_servicio("db", self.ServDB)
        self.ServicioJuego = ServicioJuego(self.Dispatcher,self.logger)


    """ VER
        *** Evaluar si va aca o en ServComunicacion
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
        """
