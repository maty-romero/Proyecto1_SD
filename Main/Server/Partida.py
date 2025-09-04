import random
import string

from Main.Server import Ronda
from Main.Server.Jugador import Jugador


class Partida:
    def __init__(self):
        self.categorias = ["Nombres", "Paises o ciudades", "Objetos"]
        self.rondas_maximas = 3 # mandar por constructor?
        self.rondas_stack: list[Ronda] = [] # Pendiente - Actua como pila
        self.jugadores = []

        """
        stack = []
        stack.append(1) # Push
        stack[-1]       # Peek -- retrieve top but not modify
        stack.pop()     # Pop -- retrieve top modifying
        """
    def get_ronda_mas_reciente(self):
        return self.rondas_stack[-1]

    # Se asume que hay jugadores requeridos para jugar
    def cargar_jugadores_partida(self, jugadores: list[Jugador]):
        self.jugadores = jugadores

    def get_jugador_mayor_puntaje(self):
        pass

    def iniciar_nueva_ronda(self): # Push in Stack
        pass # Crear instancia Ronda y pasar por ctor args --> Uso de Append pensado uso de Stack

    def get_letras_jugadas(self) -> list[str]:
        pass # Recorrer Rondas y armar listas con letras jugadas

    def get_jugadores_partida(self):
        return self.jugadores

    # GETS INFO
    def get_info_sala(self):
        nicknames = [jugador.nickname for jugador in self.jugadores]
        info = {
            "categorias": self.categorias,
            "jugadores": nicknames,
            "rondas": len(self.rondas)
        }
        return info;

    # PENDIENTE - NroRondaActual
    def get_info_ronda(self):
        info = {
            "categorias": self.categorias,
            "nro_ronda": self.rondaActual,
            "letra_ronda": self.letras_jugadas[-1],
            "letras_jugadas": self.letras_jugadas
        }
        return info

    
    





