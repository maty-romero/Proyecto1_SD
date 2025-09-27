import socket
import threading
import time

from Cliente.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Utils.ComunicationHelper import ComunicationHelper

class ManejadorSocketServidor:
    def __init__(self, host, puerto: int, callback_mensaje):
        self.host = host
        self.puerto = puerto
        self.callback_mensaje = callback_mensaje
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conexiones = []  # conexiones a múltiples réplicas
        self._escuchando = False
        self.logger = ConsoleLogger(name=f"SocketServidor[{host}:{puerto}]", level="INFO")
        self.logger.info("Nueva Instancia Sesion Socket NodoPpal")
        self.socket_listo_event = threading.Event()
        self.hilo_heartbeat = None

    def iniciar(self):
        self.socket.bind((self.host, self.puerto))
        self.socket.listen()
        self._escuchando = True
        threading.Thread(target=self._aceptar, daemon=True).start()

        # Lanzamos el hilo de heartbeat
        self.hilo_heartbeat = threading.Thread(target=self._enviar_heartbeat, daemon=True)
        self.hilo_heartbeat.start()

    def _aceptar(self):
        while self._escuchando:
            conn, addr = self.socket.accept()
            self.conexiones.append(conn)
            self.logger.info(f"Replica conectada desde {addr}")
            threading.Thread(target=self._escuchar, args=(conn,), daemon=True).start()

    def _escuchar(self, conn):
        while self._escuchando:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                self.callback_mensaje(data.decode())
            except OSError:
                break
        conn.close()

    def broadcast(self, mensaje: str):
        for conn in list(self.conexiones):  # iterar sobre copia por si alguna se cierra
            try:
                conn.sendall(mensaje.encode())
            except Exception:
                self.logger.error("Error al enviar mensaje a réplica")
                self.conexiones.remove(conn)

    def _enviar_heartbeat(self):
        while self._escuchando:
            self.logger.info("Enviando HEARTBEAT a todas las réplicas...")
            self.broadcast("HEARTBEAT")
            time.sleep(5)  # intervalo configurable

    def cerrar(self):
        self._escuchando = False
        for conn in self.conexiones:
            conn.close()
        self.socket.close()
