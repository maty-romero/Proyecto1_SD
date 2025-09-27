import socket
import threading
import time

from Cliente.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Utils.ComunicationHelper import ComunicationHelper

import socket
import threading
import time
from datetime import datetime, timedelta
from Servidor.Utils.ConsoleLogger import ConsoleLogger

class ManejadorSocket:
    def __init__(self, host: str, puerto: int, callback_mensaje, nombre_logico: str, es_servidor=False):
        self.host = host
        self.puerto = puerto
        self.callback_mensaje = callback_mensaje
        self.es_servidor = es_servidor

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conexiones = []  # lista de sockets conectados (para broadcast)
        self._escuchando = False
        self.logger = ConsoleLogger(name=f"Socket[{nombre_logico}]", level="INFO")
        self.hilo_heartbeat = None

        # Estado para algoritmo Bully
        self.coordinador = None
        self.timestamp = None
        self.conectado = False

    # ---------------------------
    # Inicializar como servidor
    # ---------------------------
    def iniciar_servidor(self):
        self.socket.bind((self.host, self.puerto))
        self.socket.listen()
        self._escuchando = True
        self.logger.info(f"Servidor escuchando en {self.host}:{self.puerto}")
        threading.Thread(target=self._aceptar_conexiones, daemon=True).start()

        # Thread de heartbeat
        self.hilo_heartbeat = threading.Thread(target=self._enviar_heartbeat, daemon=True)
        self.hilo_heartbeat.start()

    # ---------------------------
    # Conectar como cliente a otro nodo
    # ---------------------------
    def conectar_a_nodo(self, ip_destino, puerto_destino):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((ip_destino, puerto_destino))
            self.logger.info(f"Conectado a nodo en {ip_destino}:{puerto_destino}")
            self.conexiones.append(conn)
            threading.Thread(target=self._escuchar, args=(conn,), daemon=True).start()
        except Exception as e:
            self.logger.error(f"Error al conectar con nodo: {e}")

    # ---------------------------
    # Aceptar nuevas conexiones (modo servidor)
    # ---------------------------
    def _aceptar_conexiones(self):
        while self._escuchando:
            conn, addr = self.socket.accept()
            self.conexiones.append(conn)
            self.logger.info(f"Nodo conectado desde {addr}")
            threading.Thread(target=self._escuchar, args=(conn,), daemon=True).start()

    # ---------------------------
    # Escucha de mensajes
    # ---------------------------
    def _escuchar(self, conn):
        while self._escuchando:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                mensaje = data.decode()
                if mensaje == "HEARTBEAT":
                    self.timestamp = datetime.utcnow()
                    self.conectado = True
                self.callback_mensaje(mensaje, conn)
            except OSError:
                break
        conn.close()

    # ---------------------------
    # Enviar mensajes
    # ---------------------------
    def enviar(self, mensaje: str, conn=None):
        try:
            data = mensaje.encode()
            if conn:
                conn.sendall(data)
            else:
                # broadcast si no se especifica conexión
                for c in list(self.conexiones):
                    try:
                        c.sendall(data)
                    except:
                        self.logger.warning("Conexión rota, eliminando")
                        self.conexiones.remove(c)
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje: {e}")

    # ---------------------------
    # Heartbeat
    # ---------------------------
    def _enviar_heartbeat(self):
        while self._escuchando:
            self.enviar("HEARTBEAT")
            time.sleep(3)

    def esta_vivo(self) -> bool:
        if not self.conectado:
            return False
        if not self.timestamp:
            return False
        return datetime.utcnow() - self.timestamp < timedelta(seconds=5)

    def cerrar(self):
        self.logger.info("Cerrando manejador de socket...")
        self._escuchando = False
        for conn in self.conexiones:
            conn.close()
        self.socket.close()
