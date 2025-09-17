import uuid
from Servidor.Comunicacion.ManejadorSocket import ManejadorSocket
from datetime import datetime, timedelta

class ClienteConectado:
    def __init__(self, nickname: str, nombre_logico: str, ip_cliente: str, puerto_cliente: int):
        self.id = str(uuid.uuid4())
        self.nickname = nickname
        self.proxy = nombre_logico
        self.confirmado: bool = False
        self.conectado: bool = False
        self.timestamp: datetime

        self.socket = ManejadorSocket( # sesion cliente
            ip_cliente=ip_cliente,
            puerto_cliente=puerto_cliente,
            nickname_log=nickname
        )
        # Inyecta el callback como lambda
        self.socket.callback_mensaje = lambda msg: self._procesar_mensaje(msg)


    def _procesar_mensaje(self, mensaje: str):
        if mensaje == "HEARTBEAT":
            self.timestamp = datetime.utcnow()
            self.conectado = True
        else:
            pass # Otro tipo de mensajes desde el cliente?

    def esta_vivo(self) -> bool:
        if not self.conectado:
            return False
        if not self.timestamp:
            return False
        # timestamp menor a 35 seg ? False => Se asume que murio
        return datetime.utcnow() - self.timestamp < timedelta(seconds=35)


