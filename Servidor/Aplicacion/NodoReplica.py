"""
-Falta implementar hilo de escucha
-Falta implementar metodo que calcule el timeout del servidor

"""
# ---------------- NodoReplica ----------------
import sys
import threading
from time import sleep
from datetime import datetime

import Pyro5
from Servidor.Aplicacion.Nodo import Nodo
from Servidor.Comunicacion.ManejadorSocket import ManejadorSocket
from Servidor.Comunicacion.ServicioComunicacion import ServicioComunicacion
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Dominio import ServicioJuego
from Servidor.Persistencia.ControladorDB import ControladorDB
from Servidor.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.EstadoNodo import EstadoNodo


class NodoReplica(Nodo):
    def __init__(self, id, host, puerto, nombre="Replica", esCoordinador=False):
        super().__init__(id, host, puerto, nombre, esCoordinador)
        self.Dispatcher = Dispatcher()
        self.ServComunic = ServicioComunicacion(self.Dispatcher)
        self.ServDB = ControladorDB()
        self.ServicioJuego = None
        self.socket_manager: ManejadorSocket = None
        self.logger = ConsoleLogger(name=f"Replica-{self.id}", level="INFO")

        self.coordinador_actual = None
        self.heartbeat_interval = 5
        self.timeout_heartbeat = 10
        self.ultimo_heartbeat = datetime.utcnow()

    # ---------------- Inicialización como coordinador ----------------
    def iniciar_como_coordinador(self, ip_ns, puerto_ns):
        try:
            ns = Pyro5.api.locate_ns(ip_ns, puerto_ns)
            self.logger.info("Servidor de nombres localizado correctamente.")
        except Exception as e:
            self.logger.error(f"No se pudo conectar al servidor de nombres: {e}")
            sys.exit(1)
        
        self.ServicioJuego = ServicioJuego(self.Dispatcher,self.logger)

        self.Dispatcher.registrar_servicio("juego", self.ServicioJuego)
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComunic)
        self.Dispatcher.registrar_servicio("db", self.ServDB)
        self.logger.info(f"Nodo {self.get_nombre_completo()} inicializado como coordinador")
        self.socket_manager = ManejadorSocket(self.host, self.puerto, self.callback_mensaje)
        self.socket_manager.iniciar()

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

    # ---------------- Conectarse a coordinador ----------------
    def conectarse_a_coordinador(self, nodo_coordinador):
        self.logger.info(f"{self.get_nombre_completo()} conectándose a coordinador {nodo_coordinador.get_nombre_completo()}")
        self.socket_manager = ManejadorSocket(nodo_coordinador.host, nodo_coordinador.puerto, self.callback_mensaje)
        self.socket_manager.conectar()
        self.coordinador_actual = nodo_coordinador.id

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
        nodos_mayores = [n for n in self.ServComunic.nodos_cluster if n.id > self.id and n.obtener_estado() == EstadoNodo.ACTIVO]
        if not nodos_mayores:
            self.logger.info("No hay nodos mayores activos. Me proclamo coordinador.")
            self.convertirse_en_coordinador()
            return

        for nodo in nodos_mayores:
            try:
                self.socket_manager.enviar(f"ELECCION:{self.id}")
            except Exception as e:
                self.logger.warning(f"Error al enviar ELECCION a nodo {nodo.id}: {e}")

        threading.Timer(3, self.convertirse_en_coordinador).start()

    def convertirse_en_coordinador(self):
        self.coordinador_actual = self.id
        self.set_esCoordinador(True)
        self.logger.warning(f"{self.get_nombre_completo()} se convierte en coordinador")
        for nodo in self.ServComunic.nodos_cluster:
            try:
                if nodo.socket_manager:
                    nodo.socket_manager.enviar(f"COORDINADOR:{self.id}")
            except:
                pass

    # ---------------- Callback de mensajes ----------------
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
        elif mensaje.startswith("COORDINADOR"):
            coord_id = int(mensaje.split(":")[1])
            self.coordinador_actual = coord_id
            self.set_esCoordinador(self.id == coord_id)
            self.logger.info(f"Nuevo coordinador: {coord_id}")



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