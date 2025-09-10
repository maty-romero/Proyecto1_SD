import random
import string

from Main.Server import Ronda
from Main.Common.Jugador import Jugador
from enum import Enum,auto

"""----------Clase Estatica estados-----------------------------------------------------------------------------------------------------------"""
class EstadoJuego(Enum):
    #Estados fuera de la ronda
    ESPERANDO_JUGADORES = auto()
    FINALIZADO = auto()
    MOSTRANDO_RESULTADOS_FINALES = auto()

    #Estados dentro de la ronda
    RONDA_EN_CURSO = auto()
    ESPERANDO_VOTACIONES = auto()
    MOSTRANDO_RESULTADOS_RONDA = auto()

    """Otros estados posibles:
    INICIANDO - Para configuración inicial
    PAUSADA - Para manejar desconexiones
    CANCELADA - Para partidas abortadas
    VOTACIONES_CERRADAS - Para validar que no lleguen más votos
    PREPARANDO_RONDA - Para setup entre rondas
    """
"""---------------------------------------------------------------------------------------------------------------------"""

class Partida:

    def __init__(self,cat=None,ronda_actual=None,estado_actual=None,max_rondas=3):
        """ Puede utilizarse el constructor para restaurar una ronda de la base de datos"""
        self.categorias = cat or ["Nombres", "Paises o ciudades", "Objetos"]
        self.rondas_maximas = max_rondas
        self.jugadores = []
        self.ronda_actual = ronda_actual
        if estado_actual is None:
            self.estado_actual = EstadoJuego.ESPERANDO_JUGADORES
        else:
            self.estado_actual = estado_actual
        """
        stack = [] 
        stack.append(1) # Push
        stack[-1]       # Peek -- retrieve top but not modify
        stack.pop()     # Pop -- retrieve top modifying
        """
    # def get_ronda_mas_reciente(self):
    #     return self.rondas_stack[-1]

    # Se asume que hay jugadores requeridos para jugar
    def cargar_jugadores_partida(self, jugadores: list[Jugador]):
        self.jugadores = jugadores

    def get_jugador_mayor_puntaje(self):
        pass

    def iniciar_nueva_ronda(self): # Push in Stack
        pass # Crear instancia Ronda y pasar por ctor args --> Uso de Append pensado uso de Stack
        if len(self.jugadores) >= 2:
                self.estado_actual = EstadoJuego.RONDA_EN_CURSO

    #Solo guardamos ultima ronda, por lo que podria borrarse
    def get_letras_jugadas(self) -> list[str]:
        pass # Recorrer Rondas y armar listas con letras jugadas

    def get_jugadores_partida(self):
        return self.jugadores

    # GETS INFO
    def get_info_sala(self, jugadores_sala: list[Jugador]):
        nicknames = [jugador.nickname for jugador in jugadores_sala]
        info = {
            "categorias": self.categorias,
            "jugadores": nicknames,
            "rondas": self.rondas_maximas
        }
        return info

    # PENDIENTE - NroRondaActual
    def get_info_ronda(self):
        info = {
            "categorias": self.categorias,
            "nro_ronda": self.rondaActual,
            "letra_ronda": self.letras_jugadas[-1],
            "letras_jugadas": self.letras_jugadas
        }
        return info

    def esta_terminada(self) -> bool:
        return self.estado_actual == EstadoJuego.FIN_JUEGO
    
    





