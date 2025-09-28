"""
-Falta implementar hilo de escucha
-Falta implementar metodo que calcule el timeout del servidor

"""
# ---------------- NodoReplica ----------------
import socket
import sys
import threading
from time import sleep
from datetime import datetime

import Pyro5
from Servidor.Utils.ComunicationHelper import ComunicationHelper
from Servidor.Aplicacion.Nodo import Nodo
from Servidor.Comunicacion.ManejadorSocket import ManejadorSocket
from Servidor.Comunicacion.ServicioComunicacion import ServicioComunicacion
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Dominio.ServicioJuego import ServicioJuego
from Servidor.Persistencia.ControladorDB import ControladorDB
from Servidor.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.EstadoNodo import EstadoNodo


class NodoReplica(Nodo):
    def __init__(self, id, host, puerto, nombre="Replica", esCoordinador=False):
        #super().__init__(id, host, puerto, nombre, esCoordinador)
        super().__init__(id=id, host=host, puerto=puerto, nombre=nombre, esCoordinador=esCoordinador)
        self.logger = ConsoleLogger(name=f"Replica-{self.id}", level="INFO")
        self.Dispatcher = Dispatcher()
        self.ServComunic = ServicioComunicacion(self.Dispatcher)
        self.ServDB = ControladorDB()
        self.ServicioJuego = None
        # Callback_manejaje en None por default
        self.socket_manager = ManejadorSocket(host=self.host, puerto=self.puerto,
                nombre_logico=self.get_nombre_completo(), es_servidor=False)
       

        self.coordinador_actual = None
        self.heartbeat_interval = 5
        self.timeout_heartbeat = 10
        self.ultimo_heartbeat = datetime.utcnow()

        self.logger.error(f"Valor host pasado: {host};tipo:{type(host)}")
        self.logger.error(f"Valor puerto pasado: {puerto};tipo:{type(puerto)}")

    # ---------------- Inicialización como replica ----------------
    def iniciar_como_replica(self):
        """
        1. Conectarse a coordinador 
        2. Recepcionar Heartbeat y actualizar timestamp etc 
        """
        pass 


    # ---------------- Inicialización como coordinador ----------------
    def iniciar_como_coordinador(self, ip_ns, puerto_ns):
        # ns = None
        # while True or not ns:
        #     try:
        #         ns = Pyro5.api.locate_ns(ip_ns, puerto_ns)
        #         self.logger.info("Servidor de nombres localizado correctamente.")
        #     except Exception as e:
        #         self.logger.error(f"No se pudo conectar al servidor de nombres: {e}")
        #     respuesta = input("¿Deseás buscar el name server de nuevo? (s/n): ").strip().lower()
        #     if respuesta != "s" :
        #         self.logger.info("Eligio no buscar name server o se encontro name server")
        #         break
        #     self.logger.info("Buscando replica de nuevo...")
        #ns = Pyro5.api.locate_ns(ip_ns, puerto_ns)
        ns = Pyro5.api.locate_ns()
        self.logger.info(f"Servidor de nombres en: {ns}")

        self.ServicioJuego = ServicioJuego(self.Dispatcher)

        self.Dispatcher.registrar_servicio("juego", self.ServicioJuego)
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComunic)
        self.Dispatcher.registrar_servicio("db", self.ServDB)
        self.logger.info(f"Nodo {self.get_nombre_completo()} inicializado como coordinador")
        
        self.socket_manager = ManejadorSocket(
            host=self.host, puerto=self.puerto, callback_mensaje=self.callback_mensaje, nombre_logico=self.get_nombre_completo(), es_servidor=True)
        
        self.socket_manager.iniciar_manejador()

        # BD inicial de prueba
        datos = {
            "codigo": 1,
            "clientes": {"Ana": "", "Luis": {"ip": "", "puerto": "", "uri": ""}},
            "nro_ronda": 1,
            "categorias": ["Animal", "Ciudad", "Color"],
            "letra": "M",
            "respuestas": []
        }
        self.ServDB.crear_partida(datos)
        self.logger.info(f"BD inicializada: {self.ServDB.obtener_partida()}")

        threading.Thread(target=self._enviar_heartbeat, daemon=True).start()
        daemon = Pyro5.server.Daemon(socket.gethostbyname(socket.gethostname()))

        uri = ComunicationHelper.registrar_objeto_en_ns(
            self,
            "gestor.partida",
            daemon
        )

        self.logger.info("ServicioJuego registrado correctamente.")
        self.logger.debug(f"URI: {uri}")
        self.logger.debug(f"Daemon: {daemon}")
        daemon.requestLoop()

    # ---------------- Registrar Vecinos ----------------
    def registrar_nodo(self, id, nombre, ip, puerto):
        self.ServComunic.registrar_nodo(Nodo(id,nombre,ip,puerto,False))

    # ---------------- Conectarse a coordinador ----------------
    def conectarse_a_coordinador(self, nodo_coordinador):
        self.logger.info(f"{self.get_nombre_completo()} conectándose a coordinador {nodo_coordinador.get_nombre_completo()}")
        # No se utiliza la misma instancia de ManejadorSocket (ya abierta)
        #self.socket_manager = ManejadorSocket(nodo_coordinador.host, nodo_coordinador.puerto, self.callback_mensaje)
        self.socket_manager.conectar_a_nodo(nodo_coordinador.host, nodo_coordinador.puerto)
        self.coordinador_actual = nodo_coordinador.id

    # ---------------- Conectarse a replicas ----------------
    def conectarse_a_replicas(self):
        self.logger.info(f"{self.get_nombre_completo()} conectándose a las replicas...")
        # No se utiliza la misma instancia de ManejadorSocket (ya abierta)
        #self.socket_manager = ManejadorSocket(nodo_coordinador.host, nodo_coordinador.puerto, self.callback_mensaje)
        nodos_replicas = self.ServComunic.obtener_nodos_cluster()
        for replica in nodos_replicas:
            self.socket_manager.conexiones = [] # limpiar conexion previas
            self.socket_manager.conectar_a_nodo(replica.host, replica.puerto)

        #self.coordinador_actual = nodo_coordinador.id

    # ---------------- Heartbeat ----------------
   


    def _enviar_heartbeat(self):
        while True:
            sleep(self.heartbeat_interval)
            if self.socket_manager:
                try:
                    self.socket_manager.enviar("HEARTBEAT")
                except Exception as e:
                    self.logger.warning(f"No se pudo enviar heartbeat: {e}")

    def verificar_heartbeat(self):
        delta = (datetime.utcnow() - self.ultimo_heartbeat).total_seconds()
        if delta > self.timeout_heartbeat:
            self.logger.warning("No se recibió heartbeat del coordinador. Iniciando elección...")
            self.iniciar_eleccion()

    # ---------------- Bully ----------------
    def iniciar_eleccion(self):
        self.logger.info(f"{self.get_nombre_completo()} inicia elección Bully")

        self.socket_manager.iniciar_manejador() # apertura socket para escucha

        nodos_mayores = [n for n in self.ServComunic.nodos_cluster if n.id > self.id and n.obtener_estado() == EstadoNodo.ACTIVO]
        if not nodos_mayores:
            self.logger.info("No hay nodos mayores activos. Me proclamo coordinador.")
            self.socket_manager.cerrar() # no va a  recibir mensajes
            self.convertirse_en_coordinador()
            return

        

        for nodo in nodos_mayores:
            try:
                self.socket_manager.conectar_a_nodo(nodo.host, nodo.puerto)
                self.socket_manager.enviar(f"ELECCION:{self.id}")
            except Exception as e:
                self.logger.warning(f"Error al enviar ELECCION a nodo {nodo.id}: {e}")

        threading.Timer(3, self.convertirse_en_coordinador).start()

    def convertirse_en_coordinador(self):
        self.set_esCoordinador(True)
        self.logger.warning(f"{self.get_nombre_completo()} se convierte en coordinador")
        #broadcast coordinacion
        # for nodo in self.ServComunic.nodos_cluster:
        #     try:
        #         if nodo.socket_manager:
        #             nodo.socket_manager.enviar(f"COORDINADOR:{self.id}")
        #     except:
        #         pass

        # establecer conexion con nodos que son replicas (ya tienen socket abierto se supone)
        self.conectarse_a_replicas() # lista conexiones actualizada
        # Mandar mensaje a resto de replicas / nodos que este nodo es coordinador --> braodcast
        self.socket_manager.enviar(f"COORDINADOR:{self.id}")

        self.iniciar_como_coordinador(self.host, self.puerto)

    # ---------------- Callback de mensajes ----------------
    def callback_mensaje(self, mensaje, conn=None):
        self.logger.info(f"[{self.get_nombre_completo()}] Mensaje recibido: {mensaje}")
        if mensaje == "HEARTBEAT":
            self.ultimo_heartbeat = datetime.utcnow()
        elif mensaje.startswith("ELECCION"):
            remitente_id = int(mensaje.split(":")[1])
            if remitente_id < self.id: # replica que recibe mensaje tiene ID mas grande
                self.socket_manager.enviar(f"RESPUESTA:{self.id}")
                self.iniciar_eleccion()
        elif mensaje.startswith("RESPUESTA"):
            self.logger.info("Nodo mayor respondió. Esperando COORDINADOR...")
            # socket queda abierto para conexion que debe hacer nodo ppal -> Funcionamiento 'normal' 
        elif mensaje.startswith("COORDINADOR"):
            # hay un nuevo coordinador, que no es el nodo actual
            self.logger.warning(f"MENSAJE DE CORDINAAADOROOROR => {mensaje}")
            coord_id = int(mensaje.split(":")[1])
            self.coordinador_actual = coord_id
            #self.set_esCoordinador(self.id == coord_id) # esto lo deberia hacer el coordinador 
            self.logger.info(f"Nuevo coordinador: {coord_id}")
            self.iniciar_como_replica() # PENDIENTE

    #def broadcast_a_nodos(self):
        #self.socket_manager
        #pass

    # def broadcast_a_nodos(self, mensaje: str):
    #     for nodo in self.ServComunic.nodos_cluster:
    #         try:
                    
    #                 self.socket_manager.enviar(mensaje)
    #         except Exception as e:
    #             self.logger.warning(f"No se pudo enviar mensaje a nodo {nodo.get_nombre_completo()}: {e}")


    # def enviar_a_nodo(self, id_nodo: int, mensaje: str):
    #     nodo = self.obtener_nodo_por_id(id_nodo)
    #     if nodo:
    #         conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         conn.connect((ip, puerto))
    #         self.socket_manager.enviar(mensaje)
    #     else:
    #         self.logger.warning(f"No se pudo enviar mensaje. Nodo {id_nodo} no encontrado o desconectado")


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