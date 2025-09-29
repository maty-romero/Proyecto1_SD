"""
-Falta implementar hilo de escucha
-Falta implementar metodo que calcule el timeout del servidor

"""
# ---------------- NodoReplica ----------------
import socket
import sys
import threading
from time import sleep, time
from datetime import datetime
from Servidor.Aplicacion.EstadoNodo import EstadoNodo
import Pyro5
from Utils.ComunicationHelper import ComunicationHelper
from Servidor.Aplicacion.Nodo import Nodo
from Utils.ManejadorSocket import ManejadorSocket
from Servidor.Comunicacion.ServicioComunicacion import ServicioComunicacion
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Dominio.ServicioJuego import ServicioJuego
from Servidor.Persistencia.ControladorDB import ControladorDB
from Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.EstadoNodo import EstadoNodo


class NodoReplica(Nodo):
    def __init__(self, id, host, puerto, nombre="Replica", esCoordinador=False):
        super().__init__(id=id, host=host, puerto=puerto, nombre=nombre, esCoordinador=esCoordinador)
        self.logger = ConsoleLogger(name=f"Replica-{self.id}", level="INFO")
        self.Dispatcher = Dispatcher()
        self.ServComunic = ServicioComunicacion(self.Dispatcher)
        self.ServDB = ControladorDB()
        self.ServicioJuego = None

        self.socket_manager = ManejadorSocket(
            host=self.host,
            puerto=self.puerto,
            nombre_logico=self.get_nombre_completo(),
            es_servidor=False
        )

        self.coordinador_actual = None
        self.heartbeat_interval = 5
        self.timeout_heartbeat = 10
        self.ultimo_heartbeat = datetime.utcnow()

    # ---------------- Registrar Vecinos ----------------
    def registrar_nodo(self, id, nombre, ip, puerto):
        self.ServComunic.registrar_nodo(Nodo(id,nombre,ip,puerto,False))

    # ---------------- Inicialización como réplica ----------------
    def iniciar_como_replica(self):
        self.logger.info(f"{self.get_nombre_completo()} iniciando como réplica")
        threading.Thread(target=self._escuchar_heartbeat, daemon=True).start()

    def _escuchar_heartbeat(self):
        while True:
            sleep(self.heartbeat_interval)
            self.verificar_heartbeat()

    # ---------------- Inicialización como coordinador ----------------
    def iniciar_como_coordinador(self, ip_ns, puerto_ns):
        self.logger.info(f"conexiones activas:{self.socket_manager.conexiones}")

        ns = Pyro5.api.locate_ns() #ns = Pyro5.api.locate_ns(ip_ns, puerto_ns)
        self.logger.info(f"Servidor de nombres en: {ns}")

        self.ServicioJuego = ServicioJuego(self.Dispatcher)
        self.Dispatcher.registrar_servicio("juego", self.ServicioJuego)
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComunic)
        self.Dispatcher.registrar_servicio("db", self.ServDB)

        self.logger.info(f"Nodo {self.get_nombre_completo()} inicializado como coordinador")
        self.socket_manager.iniciar_manejador()

        datos = {
            "codigo": 1,
            "clientes": {"Ana": "", "Luis": {"ip": "", "puerto": "", "uri": ""}},
            "nro_ronda": 1,
            "categorias": ["Animal", "Ciudad", "Color"],
            "letra": "M",
            "respuestas": []
        }
        self.ServDB.crear_partida(datos)

        threading.Thread(target=self._enviar_heartbeat, daemon=True).start()

        daemon = Pyro5.server.Daemon(socket.gethostbyname(socket.gethostname()))
        uri = ComunicationHelper.registrar_objeto_en_ns(self.ServicioJuego, "gestor.partida", daemon)
        self.logger.info("ServicioJuego registrado correctamente.")
        daemon.requestLoop()

        #deja de aceptar conexiones una vez que se volvio coordinador
        self.socket_manager.cerrar()

    # ---------------- Conexión ----------------
    def conectarse_a_coordinador(self, nodo_coordinador):
        self.logger.info(f"{self.get_nombre_completo()} conectándose a coordinador {nodo_coordinador.get_nombre_completo()}")
        self.socket_manager.conectar_a_nodo(nodo_coordinador.host, nodo_coordinador.puerto)
        self.coordinador_actual = nodo_coordinador.id

    def conectarse_a_replicas(self):
        self.logger.info(f"{self.get_nombre_completo()} conectándose a las réplicas...")
        #limpia conexiones previamente
        for conn in self.socket_manager.conexiones:
            try:
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
            except Exception as e:
                self.logger.warning(f"Error al cerrar conexión previa: {e}")
        self.socket_manager.conexiones = []
        for replica in self.ServComunic.obtener_nodos_cluster():
            self.socket_manager.conectar_a_nodo(replica.host, replica.puerto)

    # ---------------- Heartbeat ----------------
    def _enviar_heartbeat(self):
        while True:
            sleep(self.heartbeat_interval)
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
        self.recibio_respuesta = False
        self.socket_manager.iniciar_manejador()

        nodos_mayores = [n for n in self.ServComunic.nodos_cluster if n.id > self.id and n.obtener_estado() == EstadoNodo.ACTIVO]

        if not nodos_mayores:
            self.logger.info("No hay nodos mayores activos. Me proclamo coordinador.")
            self.convertirse_en_coordinador()
            return

        for nodo in nodos_mayores:
            try:
                self.socket_manager.conectar_a_nodo(nodo.host, nodo.puerto)
                self.socket_manager.enviar(f"ELECCION:{self.id}")
            except Exception as e:
                self.logger.warning(f"Error al enviar ELECCION a nodo {nodo.id}: {e}")

        # Esperar 5 segundos para ver si alguien responde
        # threading.Timer(5, self._evaluar_eleccion).start()


    def convertirse_en_coordinador(self):
        self.set_esCoordinador(True)
        self.logger.warning(f"{self.get_nombre_completo()} se convierte en coordinador")
        self.conectarse_a_replicas()
        self.socket_manager.enviar(f"COORDINADOR:{self.id}")
        self.iniciar_como_coordinador(self.host, self.puerto)

    def _evaluar_eleccion(self):
        if not self.recibio_respuesta:
            self.logger.info("No se recibió respuesta de nodos mayores. Me proclamo coordinador.")
            self.convertirse_en_coordinador()
        else:
            self.logger.info("Esperando que el nodo mayor se proclame coordinador.")


    # ---------------- Callback ----------------
    def callback_mensaje(self, mensaje, conn=None):
        self.logger.info(f"[{self.get_nombre_completo()}] Mensaje recibido: {mensaje}")
        if mensaje == "HEARTBEAT":
            self.ultimo_heartbeat = datetime.utcnow()
        elif mensaje.startswith("ELECCION"):
            remitente_id = int(mensaje.split(":")[1])
            if remitente_id < self.id:
                self.socket_manager.enviar(f"RESPUESTA:{self.id}")
                self.iniciar_eleccion()
        elif mensaje.startswith("RESPUESTA"):
            self.logger.info("Nodo mayor respondió. Esperando COORDINADOR...")
            self.recibio_respuesta = True
            threading.Timer(5, self._evaluar_eleccion).start()
        elif mensaje.startswith("COORDINADOR"):
            coord_id = int(mensaje.split(":")[1])
            self.coordinador_actual = coord_id
            self.logger.info(f"Nuevo coordinador: {coord_id}")
            self.iniciar_como_replica()




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