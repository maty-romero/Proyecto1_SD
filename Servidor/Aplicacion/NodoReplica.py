"""
-Falta implementar hilo de escucha
-Falta implementar metodo que calcule el timeout del servidor

"""
from time import sleep

from Servidor.Aplicacion.ManejadorSocketServidor import ManejadorSocketServidor
from Servidor.Aplicacion.Nodo import Nodo
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Comunicacion.ServicioComunicacion import ServicioComunicacion
from Servidor.Dominio.ServicioJuego import ServicioJuego
from Servidor.Persistencia.ControladorDB import ControladorDB
from Servidor.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.ManejadorSocketReplica import ManejadorSocketReplica
from Servidor.Aplicacion.ManejadorSocketServidor import ManejadorSocketServidor
from Servidor.Aplicacion.NodoServidor import NodoServidor
from Servidor.Persistencia.ControladorDB import ControladorDB
from Servidor.Utils.ConsoleLogger import ConsoleLogger
from EstadoNodo import EstadoNodo

#implementa patron de failover
class NodoReplica(NodoServidor):
    def __init__(self, id, host, puerto,nombre="Replica", esCoordinador=False):
        super().__init__(id, host=host, puerto=puerto, nombre=nombre, esCoordinador=esCoordinador)
        
        #----------Instancias para coordinador----------#
        self.ServicioJuego = None
        self.ServComunic = None
        self.Dispatcher = None
        self.socket_manager = None
        #-----------------------------------------------#
        self.ServDB = ControladorDB()
        self.socket_manager = None
        self.logger = ConsoleLogger(name=f"NodoReplica[{self.get_nombre_completo()}]", level="INFO") # Sobrescritura

    def iniciar_como_coordinador(self):
        pass
        self.Dispatcher = Dispatcher()
        self.ServComunic = ServicioComunicacion(self.Dispatcher)
        self.ServicioJuego = ServicioJuego(self.Dispatcher,self.logger)
        self.Dispatcher.registrar_servicio("juego", self.ServicioJuego)
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComunic)
        self.Dispatcher.registrar_servicio("db", self.ServDB)

        self.logger.info(f"Nodo {self.get_nombre_completo()} inicializado como principal")

        self.socket_manager = ManejadorSocketServidor(self.host, self.puerto, self._on_msg)
        self.socket_manager.iniciar()
        self.Dispatcher = Dispatcher()
        self.ServComunic = ServicioComunicacion(self.Dispatcher)
        self.ServicioJuego = ServicioJuego(self.Dispatcher,self.logger)
        self.Dispatcher.registrar_servicio("juego", self.ServicioJuego)
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComunic)
        self.Dispatcher.registrar_servicio("db", self.ServDB)

        self.logger.info(f"Nodo {self.get_nombre_completo()} inicializado como principal")

        self.socket_manager = ManejadorSocketServidor(self.host, self.puerto, self._on_msg)
        self.socket_manager.iniciar()

        #datos de prueba para testear la bd
        datos = {
            "codigo": 1,          # código de la partida
            "clientes": {
                "Ana": "",
                "Luis":{
                    "ip"
                    "puerto"
                    "uri"
                }
            },
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

    def conectarse_a_coordinador(self):
        self.logger.info(f"{self.get_nombre_completo()} conectándose a nodo primario {self.id_coordinador_actual}")
        #self.logger.error(self.nodos_cluster)
        coincidencias = [n for n in self.nodos_cluster if n.esCoordinador == self.id_coordinador_actual]
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


    #se invoca este metodo cuando no se detecto 
    # def check_failover(self, main_server):
    #     if not main_server.estado==EstadoNodo.ACTIVO:
    #         self.logger.warning(f"Se detecto fallo en el servidor. Cambiando {self.get_nombre_completo()} a nodo principal")
    #         self.active = True
    #         self.nombre = "Servidor"
    #         self.iniciar_servicio()
    #         self.logger.warning(f"El nuevo nombre de la replica es {self.get_nombre_completo()} ")
    #         # aquí conectarse o sincronizar con el NameServer


    # def sincronizar_con_servidor(self):
    #         estado = self.servidor_ref.obtener_estado()
    #         self.actualizar_estado(estado)

    #puede servir para impresiones en logger, o como registro
    # def actualizar_estado(self, datos):
    #     self.estado.update(datos)
    #     self.logger.info(f"Réplica {self.id} actualizada con datos: {datos}")