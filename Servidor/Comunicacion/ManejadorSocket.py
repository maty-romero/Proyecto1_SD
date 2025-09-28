import socket
import threading
import time
from datetime import datetime, timedelta
from Servidor.Utils.ConsoleLogger import ConsoleLogger

class ManejadorSocket:
    def __init__(self, host: str, puerto: int, nombre_logico: str, callback_mensaje = None, es_servidor=False):
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

    def set_callback(self, callback):
        self.callback_mensaje = callback

    # ---------------------------
    # Inicializar como servidor
    # ---------------------------
    def iniciar_manejador(self):
        if self._escuchando:
            self.logger.warning("El manejador ya está activo.")
            return

        # Recrear el socket si fue cerrado
        if self.socket is None or self.socket.fileno() == -1:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.puerto))
            self.socket.listen()
            self._escuchando = True
            self.logger.info(f"Servidor escuchando en {self.host}:{self.puerto}")
            threading.Thread(target=self._aceptar_conexiones, daemon=True).start()

             # verificacion de hilo vivo
            if self.hilo_heartbeat is None or not self.hilo_heartbeat.is_alive():
                self.hilo_heartbeat = threading.Thread(target=self._enviar_heartbeat, daemon=True)
                self.hilo_heartbeat.start()
        except Exception as e:
            self.logger.error(f"Error al iniciar el manejador de socket: {e}")
            self._escuchando = False
            if self.socket:
                self.socket.close()
                self.socket = None

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
            try:
                conn, addr = self.socket.accept()
                self.conexiones.append(conn)
                self.logger.info(f"Nodo conectado desde {addr}")
                threading.Thread(target=self._escuchar, args=(conn,), daemon=True).start()
            except OSError as e:
                self.logger.warning(f"Error al aceptar conexión: {e}")
                break

    # ---------------------------
    # Escucha de mensajes para el cliente y para el servidor
    # ---------------------------
    def _escuchar(self, conn):
        while self._escuchando:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                mensaje = data.decode()
                if mensaje == "HEARTBEAT": #solo es heartbeat en servidor y en replica
                    self.timestamp = datetime.utcnow()
                    self.conectado = True

                if self.callback_mensaje is not None:
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
    # Heartbeat de cliente a replica
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
            try:
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
            except Exception as e:
                self.logger.warning(f"Error al cerrar conexión: {e}")
        self.conexiones.clear()

        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except Exception as e:
                self.logger.warning(f"Error al cerrar socket principal: {e}")
            finally:
                self.socket = None
