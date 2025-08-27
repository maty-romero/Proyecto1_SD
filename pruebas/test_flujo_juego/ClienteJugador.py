""""
    Clase esqueleto para ejecucion de procedimientos
    remotos desde Server
"""
import Pyro5.api
import os

@Pyro5.api.expose
class ClienteJugador:
    def __init__(self, nickname):
        self.nickname = nickname

    def recibir_info_sala(self, info: str):
        # Limpiar la consola -- No limpia
        os.system('cls' if os.name == 'nt' else 'clear')

        # Mostrar el mensaje recibido
        print(f"🟢 Server mandó mensaje!\n📨 Mensaje: {info}")
