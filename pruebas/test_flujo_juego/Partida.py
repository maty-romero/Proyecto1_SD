import json

class Partida:
    def __init__(self):
        self.jugadores = {}
        self.categorias = ["Nombres", "Paises o ciudades", "Objetos"]
        self.rondas = 3 # nro rondas

    def agregar_jugador_partida(self, nickname, objeto_cliente_remoto):
        self.jugadores[nickname] = objeto_cliente_remoto

    # devuelve objeto remoto del cliente
    def get_jugador(self, nickname: str):
        return self.jugadores[nickname]

    def get_info_partida_json(self):
        info = {
            "Categorias": self.categorias,
            "jugadores": list(self.jugadores.keys()),
            "rondas": self.rondas
        }
        return json.dumps(info, indent=4)

    def is_nickname_disponible(self, nickname: str):
        if nickname in self.jugadores:
            return False
        return True


