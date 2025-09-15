import socket
import threading

from Cliente.Utils.ConsoleLogger import ConsoleLogger


class ManejadorSocket:
    def __init__(self, host, puerto, callback_mensaje):
        self.host = host # Dirección IP del servidor
        self.puerto = puerto    # Puerto del servidor
        self.callback_mensaje = callback_mensaje # Función para manejar mensajes entrantes
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket TCP
        self.conexion = None
        self.hilo = None
        self._escuchando = False
        self.logger = ConsoleLogger(name="ManejadorSocket", level="INFO") # cambiar si se necesita 'DEBUG'

    @staticmethod
    def obtener_puerto_libre(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))  # 0 = que el SO elija un puerto libre
        puerto = s.getsockname()[1]
        s.close()
        self.puerto = puerto
        return puerto

    def iniciar(self):
        """Inicia el socket y comienza a escuchar un cliente."""
        self.socket.bind((self.host, self.puerto))
        self.socket.listen(1)
        self.logger.info(f"Esperando en {self.host}:{self.puerto}")
        self.conexion, addr = self.socket.accept()
        self.logger.info(f"Cliente conectado desde {addr}")
        self._escuchando = True
        self.hilo = threading.Thread(target=self._escuchar, daemon=True)
        self.hilo.start()

    def enviar(self, mensaje: str):
        """Envía un mensaje al cliente conectado."""
        if self.conexion:
            self.logger.info(f"Enviando mensaje a cliente")
            self.conexion.sendall(mensaje.encode())

    def _escuchar(self):
        """Loop de escucha en un hilo separado."""
        while self._escuchando:
            try:
                data = self.conexion.recv(1024)
                if not data:
                    break
                self.callback_mensaje(data.decode())
            except OSError:
                break
        self.cerrar()

    def esta_conectado(self) -> bool:
        """Devuelve True si el cliente está conectado."""
        return self.conexion is not None

    def cerrar(self):
        """Cierra la conexión y detiene el hilo."""
        self._escuchando = False
        if self.conexion:
            self.conexion.close()
            self.conexion = None
        self.socket.close()