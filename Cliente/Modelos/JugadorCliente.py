from Utils.ManejadorSocket import ManejadorSocket


class JugadorCliente:
    def __init__(self, nickname: str):
        self.nickname = nickname
        self.nombre_logico = f"jugador.{nickname}"
        self.sesion_socket: ManejadorSocket = None  # se inyecta desde el controlador

    def get_nickname(self):
        return self.nickname

    def get_nombre_logico(self):
        return self.nombre_logico

    def to_dict(self) -> dict:
        return {
            'nickname': self.nickname,
            'nombre_logico': self.nombre_logico,
            'ip': self.sesion_socket.host,
            'puerto': self.sesion_socket.puerto
        }