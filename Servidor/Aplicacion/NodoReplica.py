"""
-Falta implementar hilo de escucha
-Falta implementar metodo que calcule el timeout del servidor

"""
import sys
from time import sleep
from Pyro5 import errors
import Pyro5
from Pyro5.errors import NamingError, CommunicationError
from Servidor.Aplicacion.ManejadorSocketServidor import ManejadorSocketServidor
from Servidor.Aplicacion.Nodo import Nodo
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Comunicacion.ServicioComunicacion import ServicioComunicacion
from Servidor.Dominio.ServicioJuego import ServicioJuego
from Servidor.Persistencia.ControladorDB import ControladorDB
from Servidor.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.ManejadorSocketReplica import ManejadorSocketReplica
from Servidor.Aplicacion.ManejadorSocketServidor import ManejadorSocketServidor
from Servidor.Persistencia.ControladorDB import ControladorDB
from Servidor.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.EstadoNodo import EstadoNodo

#implementa patron de failover
class NodoReplica():
    def __init__(self, id, host, puerto,nombre="Replica", esCoordinador=False):
        super().__init__(id, host=host, puerto=puerto, nombre=nombre, esCoordinador=esCoordinador)
        
        #----------Instancias para coordinador----------#
        self.ServicioJuego = None
        self.socket_manager = None
        self.Dispatcher = Dispatcher()
        self.ServComunic = ServicioComunicacion(self.Dispatcher)
        #-----------------------------------------------#
        self.ServDB = ControladorDB()
        self.socket_manager = None
        self.logger = ConsoleLogger(name=f"Replica Local", level="INFO") # Sobrescritura

    def iniciar_como_coordinador(self,ip_ns,puerto_ns):
        reintentar = True
        while reintentar:
            self.logger.info("[Main] Iniciando servidor principal...")
            try:
                ns = Pyro5.api.locate_ns(ip_ns,puerto_ns)
                self.logger.info("Servidor de nombres localizado correctamente.")
                reintentar=False
            except (NamingError, CommunicationError, ConnectionRefusedError) as e:
                 self.logger.error(f"No se pudo conectar al servidor de nombres: {e}")
                 self.logger.warning("Abortando inicio del servidor.")
            
            s_n = input("Desea reintentar conexión? (s/n): ").strip().lower()
            if s_n != "s":
                sys.exit(1)

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
        # aviso a todos los nodos vecinos - nuevo coordinador (broadcast)

    # ---------------

    def verificar_heartbeat(self):
        if not self.recibe_heartbeat_a_tiempo():
            self.logger.warning("No se recibió heartbeat del coordinador. Iniciando elección...")
            self.iniciar_eleccion_coordinador() # Algoritmo Bully


    # Algoritmo de Bully 
    def iniciar_eleccion_coordinador(self): 
        self.logger.info(f"{self.get_nombre_completo()} inicia elección Bully")

        nodos_mayores = [n for n in self.nodos_cluster if n.id > self.id and self.nodo_esta_activo(n)]
        if not nodos_mayores:
            self.logger.info("No hay nodos mayores activos. Me proclamo coordinador.")
            self.proclamar_coordinador()
            return

        respuestas = []
        for nodo in nodos_mayores:
            try:
                self.enviar_mensaje_eleccion(nodo)
                respuesta = self.esperar_respuesta(nodo, timeout=2)
                if respuesta == "OK":
                    respuestas.append(nodo.id)
            except Exception as e:
                self.logger.warning(f"Fallo al contactar nodo {nodo.id}: {e}")
                self.marcar_nodo_como_inactivo(nodo)

        if not respuestas:
            self.logger.info("Nadie respondió. Me proclamo coordinador.")
            self.proclamar_coordinador()
        else:
            self.logger.info("Delego elección a nodos mayores.")

    def recibir_mensaje_eleccion(self, id_remitente):
        self.logger.info(f"Recibí mensaje de elección de nodo {id_remitente}")
        if self.id > id_remitente:
            self.enviar_respuesta_ok(id_remitente)
            self.iniciar_eleccion_coordinador()

    def enviar_mensaje_eleccion(nodo):
        pass 



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