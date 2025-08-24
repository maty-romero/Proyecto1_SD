import json

class Partida:
    def __init__(self):
        # Diccionario de jugadores: clave = IP, valor = nickname
        self.jugadores = {}  # Ejemplo: { "192.168.0.1": "Goku123" }
        self.categorias = ["Nombres", "Paises o ciudades", "Objetos"]
        self.rondas = 3 # nro rondas

    def agregar_jugador_partida(self, nickname, ip):
        self.jugadores[ip] = nickname

    def get_info_partida_json(self):
        info = {
            "Categorias": self.categorias,
            "jugadores": list(self.jugadores.keys()),
            "rondas": self.rondas
        }
        return json.dumps(info, indent=4)
