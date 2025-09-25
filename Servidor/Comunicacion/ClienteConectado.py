import sys
import uuid

import Pyro5

from Cliente.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Comunicacion.ManejadorSocket import ManejadorSocket
from datetime import datetime, timedelta

class ClienteConectado:
    def __init__(self, nickname: str, nombre_logico: str, ip_cliente: str, puerto_cliente: int):
        self.id = str(uuid.uuid4())
        self.nickname = nickname
        self.proxy = self.crear_proxy_cliente(nombre_logico)
        self.confirmado: bool = False
        self.conectado: bool = False
        self.timestamp: datetime
        self.logger = ConsoleLogger(name="ServicioComunicacion", level="INFO")

        self.socket = ManejadorSocket( # sesion cliente
            ip_cliente=ip_cliente,
            puerto_cliente=puerto_cliente,
            callback_mensaje= lambda msg: self._procesar_mensaje(msg),
            nickname_log=nickname
        )
        # Inyecta el callback como lambda
        #self.socket.callback_mensaje =

    def get_proxy_cliente(self):
        return self.proxy

    def crear_proxy_cliente(self, nombre_logico: str):
        try:
            with Pyro5.api.locate_ns(self.ip, self.puerto) as ns: 
                uri = ns.lookup(nombre_logico)
                return Pyro5.api.Proxy(uri)
        except Pyro5.errors.NamingError:
            self.logger.error(f"Error: No se pudo encontrar el objeto '{nombre_logico}'.")
            sys.exit(1)
            return None
                        


    def _procesar_mensaje(self, mensaje: str):
        if mensaje == "HEARTBEAT":
            self.logger.info(f"Heartbeat recibido del cliente/jugador '{self.nickname}'")
            self.timestamp = datetime.utcnow()
            self.conectado = True
        else:
            self.logger.info(f"Mensaje recibido: {mensaje}") # Otro tipo de mensajes desde el cliente?

    def esta_vivo(self) -> bool:
        if not self.conectado:
            return False
        if not self.timestamp:
            return False
        # timestamp menor a 35 seg ? False => Se asume que murio
        return datetime.utcnow() - self.timestamp < timedelta(seconds=3)


