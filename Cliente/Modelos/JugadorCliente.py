class JugadorCliente:
    def __init__(self, nickname: str):
        self.nickname = nickname
        self.nombre_logico = f"jugador.{nickname}"
        # otros atributos

    def get_nickname(self):
        return self.nickname

    def get_nombre_logico(self):
        return self.nombre_logico