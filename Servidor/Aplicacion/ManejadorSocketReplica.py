import socket
import threading

from Servidor.Utils.ConsoleLogger import ConsoleLogger

"""
    El servidor se conecta al socket abierto por el cliente (sesion) 
"""
class ManejadorSocketReplica:
    def __init__(self, ip_primario: str, puerto_primario: int, callback_mensaje, nickname_log: str):
        self.ip_primario = ip_primario
        self.puerto_primario = puerto_primario
        self.callback_mensaje = callback_mensaje # funcion que se ejecuta cuando ocurre un evento
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hilo_escucha = None
        self._escuchando = False
        self.logger = ConsoleLogger(name=f"ReplicaSocket[{nickname_log}]", level="INFO")

    def conectar(self):
        try:
            self.socket.connect((self.ip_primario, self.puerto_primario))
            self.logger.info(f"Conectado al nodo ppal en {self.ip_primario}:{self.puerto_primario}")
            self._escuchando = True
            self.hilo_escucha = threading.Thread(target=self._escuchar, daemon=True)
            self.hilo_escucha.start()
        except Exception as e:
            self.logger.error(f"Error al conectar: {e}")

    def enviar(self, mensaje: str):
        try:
            if isinstance(mensaje, bytes):
                self.socket.sendall(mensaje)  # ya está codificado
            else:
                self.socket.sendall(mensaje.encode())  # codificamos si es str
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
