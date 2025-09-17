import socket
import threading
import time

from Cliente.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Utils.ComunicationHelper import ComunicationHelper

class ClienteSocket:
    def __init__(self, puerto_fijo: int, callback_mensaje,nickname_log: str):
        self.host = ComunicationHelper.obtener_ip_local()
        self.puerto = puerto_fijo
        self.callback_mensaje = callback_mensaje # funcion que se ejecuta cuando ocurre un evento
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conexion = None
        self.hilo_escucha = None
        self.hilo_heartbeat = None
        self._escuchando = False
        self.logger = ConsoleLogger(name=f"ClienteSocket[{nickname_log}]", level="INFO")

    def iniciar(self):
        self.socket.bind((self.host, self.puerto))
        self.socket.listen(1)
        self.logger.info(f"Cliente esperando conexion en {self.host}:{self.puerto}")
        self.conexion, addr = self.socket.accept()
        self.logger.info(f"Servidor conectado desde {addr}")
        self._escuchando = True

        self.hilo_escucha = threading.Thread(target=self._escuchar, daemon=True)
        self.hilo_escucha.start()
        self.hilo_heartbeat = threading.Thread(target=self._enviar_heartbeat, daemon=True)
        self.hilo_heartbeat.start()

    def _escuchar(self):
        while self._escuchando:
            try:
                data = self.conexion.recv(1024)
                if not data:
                    break
                self.callback_mensaje(data.decode())
            except OSError:
                break
        self.cerrar()

    def _enviar_heartbeat(self):
        while self._escuchando:
            try:
                self.conexion.sendall(b"HEARTBEAT")
                time.sleep(30)  # cada 30 seg
            except OSError:
                break

    def cerrar(self):
        self._escuchando = False
        if self.conexion:
            self.conexion.close()
            self.conexion = None
        self.socket.close()

