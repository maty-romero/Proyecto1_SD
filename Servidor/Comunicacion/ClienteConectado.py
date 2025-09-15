class ClienteConectado:
    def __init__(self, id_cliente, socket, nombre_logico, nick, ip):
        self.id = id_cliente
        self.socket = socket
        self.proxy = nombre_logico
        self.nick = nick
        self.ip = ip
        self.confirmado = bool
        self.timestamp  # Lista de timestamps de actividad