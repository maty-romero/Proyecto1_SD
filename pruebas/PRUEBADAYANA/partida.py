import json
import random

class Partida:
    def __init__(self):
        self.jugadores = {}  # nickname: proxy_cliente
        self.categorias = ["Nombre", "Apellido", "Cosas", "Fruta", "Ciudad", "Color"]
        self.rondas = 3
        self.respuestas_ronda = {}
        self.observers = []  # Observer pattern

    def agregar_jugador_partida(self, nickname, proxy):
        self.jugadores[nickname] = proxy
        self.observers.append(proxy)

    def is_nickname_disponible(self, nickname):
        return nickname not in self.jugadores

    def get_info_partida_json(self):
        return json.dumps({
            "jugadores": list(self.jugadores.keys()),
            "categorias": self.categorias,
            "rondas": self.rondas
        }, indent=4)

    def obtener_letra_aleatoria(self):
        return random.choice("ABCDEFGHIJKLMNÑOPQRSTUVWXYZ")

    def get_info_ronda_json(self, letra, nro_ronda):
        return json.dumps({
            "letra": letra,
            "ronda": nro_ronda,
            "categorias": self.categorias
        })

    def recibir_respuestas_jugador(self, nickname, respuestas):
        self.respuestas_ronda[nickname] = respuestas

    # Observer notify
    def notificar_inicio_ronda(self, info_ronda):
        for proxy in self.observers:
            proxy.recibir_info_inicio_ronda(info_ronda)

    def notificar_fin_ronda(self, puntajes):
        for proxy in self.observers:
            proxy.recibir_info_fin_ronda(puntajes)
