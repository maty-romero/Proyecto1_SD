import sys
import uuid
import Pyro5

from Utils.ConsoleLogger import ConsoleLogger
from Utils.ManejadorSocket import ManejadorSocket
from datetime import UTC, datetime, timedelta
TIMEOUT_CLIENTE = 6
class ClienteConectado:
    def __init__(self, nickname: str, nombre_logico: str, ip_cliente: str, puerto_cliente: int,uri_cliente:str):
        self.id = str(uuid.uuid4())
        self.nickname = nickname
        self.logger = ConsoleLogger(name="ServicioComunicacion", level="INFO")
        self.uri_cliente_conectado = Pyro5.core.URI(uri_cliente)
        self.proxy = self.crear_proxy_cliente(nombre_logico,ip_cliente,puerto_cliente,uri_cliente)
        self.logger.warning(f"proxy del cliente registrada: {self.proxy}")
        self.confirmado: bool = False
        self.conectado: bool = True

        # Guardar datos para reconexión
        self.ip_cliente = ip_cliente 
        self.puerto_cliente = puerto_cliente
        self.nombre_logico = nombre_logico

        self.timestamp: datetime = datetime.now(UTC)
        self.logger.warning(f"datos del timestamp constructor{self.timestamp}")
        self.socket = ManejadorSocket(host=ip_cliente, puerto=puerto_cliente, nombre_logico=nickname)
        # Inyecta el callback como lambda
        self.socket.set_callback(self._procesar_mensaje)


    def get_proxy_cliente(self):
        return self.proxy

    def crear_proxy_cliente(self, nombre_logico: str, ip, puerto,uri):
        try:
            return Pyro5.api.Proxy(uri)    
        except:
            self.logger.error(f"Error: No se pudo encontrar el objeto '{nombre_logico}'.")
            sys.exit(1)
            return None

    def _procesar_mensaje(self, mensaje: str):
        if mensaje == "HEARTBEAT":
            self.logger.info(f"Heartbeat recibido del cliente/jugador '{self.nickname}'")
            self.timestamp = datetime.now(UTC)
            self.conectado = True
        else:
            self.logger.info(f"Mensaje recibido: {mensaje}") # Otro tipo de mensajes desde el cliente?

    def esta_vivo(self) -> bool:
        if not self.conectado:
            self.logger.debug(f"[DEBUG] {self.nickname} no está conectado (flag conectado=False)")
            return False
        if not self.timestamp:
            self.logger.debug(f"[DEBUG] {self.nickname} no tiene timestamp de heartbeat")
            return False
        # timestamp menor a 35 seg ? False => Se asume que murio
        return datetime.now(UTC) - self.timestamp < timedelta(seconds=TIMEOUT_CLIENTE)


