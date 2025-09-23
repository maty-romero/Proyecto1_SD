
from Servidor.Dominio.Jugador import Jugador
from Servidor.Dominio.Ronda import Ronda

class Partida:
    def __init__(self):
        self.categorias = ["Nombres", "Paises o ciudades", "Objetos"]
        self.rondas_maximas = 3
        self.nro_ronda_actual = 0
        self.letras_jugadas: list[str] = []
        self.ronda_actual: Ronda = None
        self.jugadores: list[Jugador] = []

    # Se asume que hay jugadores requeridos para jugar
    def cargar_jugadores_partida(self, jugadores: list[Jugador]):
        self.jugadores = jugadores

    def get_jugador_mayor_puntaje(self):
        pass

    def iniciar_nueva_ronda(self):
        self.nro_ronda_actual+= 1
        self.ronda_actual = Ronda(
            nro_ronda=self.nro_ronda_actual, categorias=self.categorias,
            jugadores=self.jugadores, letras_jugadas=self.letras_jugadas
        )

    def get_letras_jugadas(self) -> list[str]:
        pass  # Recorrer Rondas y armar listas con letras jugadas

    def get_jugadores_partida(self):
        return self.jugadores

    def eliminar_jugador_partida(self, nickname: str):
        #self.jugadores.pop() # Desconexion o fallo del cliente ?
        pass

    # GETS INFO
    def get_info_sala(self) -> dict:
        info = {
            "categorias": self.categorias,
            "rondas": self.rondas_maximas
        }
        return info

    def get_info_ronda(self):
        info = {
            "categorias": self.categorias,
            "nro_ronda": self.nro_ronda_actual,
            "letra_ronda": self.ronda_actual.letra_ronda,
            "letras_jugadas": self.letras_jugadas
        }
        return info








