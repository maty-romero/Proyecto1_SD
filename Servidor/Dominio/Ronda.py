import string
import random

from Servidor.Dominio.Jugador import Jugador


class Ronda:
    def __init__(self, nro_ronda: int, categorias: list[str], jugadores: list[Jugador], letras_jugadas: list[str]):
        self.nro_ronda = nro_ronda
        self.finalizada: bool = False
        self.letras_jugadas = letras_jugadas
        self.letra_ronda = self.get_letra_random()
        self.categorias = categorias
        self.jugadores_ronda = jugadores

    # PENDIENTE --> Completar Clase RONDA y Clase Respuesta

    def get_estado_ronda(self):
        return self.finalizada
    
    def set_estado_ronda(self, estado):
        self.finalizada = estado

    def get_letra_random(self):
        letras = list(string.ascii_uppercase)
        if len(self.letras_jugadas) <= 0:
            return random.choice(letras)

        disponibles = [l for l in letras if l not in self.letras_jugadas]

        if not disponibles:
            raise ValueError("No quedan letras disponibles")

        letra = random.choice(disponibles)
        #self.letras_jugadas.append(letra)  # Guardar la letra jugada
        return letra

    def info_ronda(self):
        info = {
            "categorias": self.categorias,
            "nro_ronda_actual":self.nro_ronda,
            "letra_ronda": self.letra_ronda,
        }
        return info

    """
    def iniciar_partida(self):
        self.rondaActual = 1
        letra = self.get_letra_random()

    """