from time import sleep
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
        self.ServDB = ControladorDB()
        #analizar posibles modificaciones a esta invocacion
        self.ServicioJuego = None
        self.ServComunic = None
        self.Dispatcher = None
        if self.activo:
            self.iniciar_servicio()

    def iniciar_servicio(self):
        self.Dispatcher = Dispatcher()
        self.ServComunic = ServicioComunicacion(self.Dispatcher)
        self.ServicioJuego = ServicioJuego(self.Dispatcher,self.logger)
        self.Dispatcher.registrar_servicio("juego", self.ServicioJuego)
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComunic)
        self.Dispatcher.registrar_servicio("db", self.ServDB)
        

        #datos de prueba para testear la bd
        datos = {
            "codigo": 1,          # código de la partida
            "jugadores": ["Ana", "Luis"],
            "nro_ronda": 1,
            "categorias": ["Animal", "Ciudad", "Color"],
            "letra": "M",
            "respuestas": [
                    { "jugador": "Ana", "Animal": "Mono", "Ciudad": "Madrid", "Color": "Marrón" },
                    { "jugador": "Luis", "Animal": "Murciélago", "Ciudad": "Montevideo", "Color": "Magenta" }
                ]
            }

        dataI = self.ServDB.obtener_partida()
        #deberia imprimir la data vacia 
        self.logger.info(dataI)
        self.ServDB.crear_partida(datos)
        #deberia imprimir la data cargada en la linea anterior
        data2 = self.ServDB.obtener_partida()
        self.logger.info(data2)
        
        RegistroControladorDB = self.ServDB.registroDatos
        self.logger.info(f"RegistroDB: {RegistroControladorDB}")
        sleep(1)


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
