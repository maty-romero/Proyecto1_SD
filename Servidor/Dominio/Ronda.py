import string
import random

from Servidor.Dominio.Jugador import Jugador


class Ronda:
    def __init__(self, nro_ronda: int, categorias: list[str], jugadores: list[Jugador], letras_jugadas: list[str]):
        self.nro_ronda = nro_ronda
        self.finalizada: bool = False
        self.letras_jugadas = letras_jugadas if letras_jugadas else []  # Solo para consulta
        self.letra_ronda = self.get_letra_random()  # La letra de ESTA ronda
        self.categorias = categorias
        self.jugadores_ronda = jugadores
        self.respuestas_ronda:dict = {}

    def set_estado_ronda(self, estado):
        self.finalizada = estado

    def set_respuestas_ronda(self,respuestas):
        self.respuestas_ronda = respuestas
    
    def get_respuestas_ronda(self):
        return self.respuestas_ronda

    def get_estado_ronda(self):
        return self.finalizada

    def get_letra_random(self):
        letras = list(string.ascii_uppercase)
        
        disponibles = [l for l in letras if l not in self.letras_jugadas]
        print(f"Las letras disponibles para jugar son {disponibles}")

        if not disponibles:
            raise ValueError("No quedan letras disponibles")
        return random.choice(disponibles)

    # def info_ronda(self): #se usa en Partida
        info = {
            "categorias": self.categorias,
            "nro_ronda_actual":self.nro_ronda,
            "letra_ronda": self.letra_ronda,
        }
        return info

    @staticmethod
    def desde_datos_bd(datos_ronda: dict, jugadores: list, letras_jugadas: list):
        """Restaura una ronda desde los datos de la base de datos"""
        ronda = Ronda.__new__(Ronda)  # Crear sin llamar __init__, porque se llamaría a get_letra_random sobreescribiendo la letra que se trajo de BD

        ronda.nro_ronda = datos_ronda.get("nro_ronda", 1)
        ronda.finalizada = datos_ronda.get("finalizada", False)
        ronda.letras_jugadas = letras_jugadas.copy() if letras_jugadas else []
        ronda.letra_ronda = datos_ronda.get("letra", "A")
        ronda.categorias = datos_ronda.get("categorias", [])
        ronda.jugadores_ronda = jugadores
        ronda.respuestas_ronda = datos_ronda.get("respuestas", {})
        
        return ronda

    """
    def iniciar_partida(self):
        self.rondaActual = 1
        letra = self.get_letra_random()

    """