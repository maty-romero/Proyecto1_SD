from Servidor.Aplicacion.Nodo import Nodo
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Comunicacion.ServicioComunicacion import ServicioComunicacion
from Servidor.Dominio.ServicioJuego import ServicioJuego
from Servidor.Persistencia.ControladorDB import ControladorDB


class NodoServidor(Nodo):
    #def __init__(self, id, ServComunic=ServicioComunicacion(), ServJuego=ServicioJuego()
    def __init__(self, id):
        super().__init__(id)
        self.Dispatcher = Dispatcher()
        self.ServComunic = ServicioComunicacion(self.Dispatcher)
        self.ServJuego = ServicioJuego(self.Dispatcher)
        self.ServJuego = ControladorDB()
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComms)
        self.Dispatcher.registrar_servicio("juego", self.ServJuego)
        self.Dispatcher.registrar_servicio("db", self.ServDB)

        # Evaluar si va aca o en ServComunicacion
        # self.replicas = [] # un servidor posee varias replicas

    def iniciar_servicio(self):
        pass


    # def registrar_replica(self, replica):
    #     self.replicas.append(replica)
    #     print(f"Replica {replica.id} registrada")

    # def propagar_actualizacion(self, datos):
    #     self.actualizar_estado(datos)
    #     for replica in self.replicas:
    #         replica.actualizar_estado(datos)

    # def consultar_bd(self, query):
    #     # Ejecuta una consulta en la base de datos
    #     pass

    # def guardar_estado_en_bd(self):
    #     # Persiste el estado actual
    #     pass