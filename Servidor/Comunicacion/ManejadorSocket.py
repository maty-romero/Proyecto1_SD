import socket
import threading

from Cliente.Utils.ConsoleLogger import ConsoleLogger

"""
    El servidor se conecta al socket abierto por el cliente (sesion) 
"""

class ManejadorSocket:
    def __init__(self, ip_cliente: str, puerto_cliente: int, callback_mensaje, nickname_log: str):
        self.ip_cliente = ip_cliente
        self.puerto_cliente = puerto_cliente
        self.callback_mensaje = callback_mensaje # funcion que se ejecuta cuando ocurre un evento
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hilo_escucha = None
        self._escuchando = False
        self.logger = ConsoleLogger(name=f"ServidorConectado[{nickname_log}]", level="INFO")

    def conectar(self):
        try:
            self.socket.connect((self.ip_cliente, self.puerto_cliente))
            self.logger.info(f"Conectado al cliente en {self.ip_cliente}:{self.puerto_cliente}")
            self._escuchando = True
            self.hilo_escucha = threading.Thread(target=self._escuchar, daemon=True)
            self.hilo_escucha.start()
        except Exception as e:
            self.logger.error(f"Error al conectar: {e}")

    def enviar(self, mensaje: str):
        try:
            self.socket.sendall(mensaje.encode())
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje: {e}")

    def _escuchar(self):
        while self._escuchando:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                self.callback_mensaje(data.decode())
            except OSError:
                break
        self.cerrar()

    def cerrar(self):
        self._escuchando = False
        self.socket.close()
