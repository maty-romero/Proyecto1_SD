
from enum import Enum, auto
from Servidor.Dominio.Jugador import Jugador
from Servidor.Dominio.Ronda import Ronda

"""----------Clase Estatica estados-----------------------------------------------------------------------------------------------------------"""
class EstadoJuego(Enum):
    #Estados fuera de la ronda
    EN_SALA = auto()
    MOSTRANDO_RESULTADOS_FINALES = auto()

    #Estados dentro de la ronda
    RONDA_EN_CURSO = auto()
    EN_VOTACIONES = auto()
"""---------------------------------------------------------------------------------------------------------------------"""

class Partida:
    def __init__(self):
        self.categorias = ["Nombres", "Animales", "Colores" ,"Paises o ciudades", "Objetos"]
        self.rondas_maximas = 2
        self.nro_ronda_actual = 0
        self.letras_jugadas: list[str] = []
        self.ronda_actual: Ronda = None
        self.jugadores: list[Jugador] = []
        self.estado_actual = EstadoJuego.EN_SALA

    def eliminar_jugador_partida(self, nickname: str):
        for jugador in self.jugadores:
            if jugador.nickname == nickname: 
                self.jugadores.remove(jugador)

    # Se asume que hay jugadores requeridos para jugar
    def cargar_jugadores_partida(self, jugadores: list[Jugador]):
        self.jugadores = jugadores

    def calcular_puntos_partida(self):
        puntajes_totales = {}
        for jugador in self.jugadores:
            puntajes_totales[jugador.nickname] = jugador.get_puntaje()

        puntaje_maximo = max(jugador.get_puntaje() for jugador in self.jugadores)
        ganadores = [jugador for jugador in self.jugadores if jugador.get_puntaje() == puntaje_maximo]

        if len(ganadores) == 1:
            ganador = ganadores[0].nickname
        else:
            ganador = f"Empate entre: {', '.join([g.nickname for g in ganadores])}"

        return puntajes_totales, ganador

    def iniciar_nueva_ronda(self):
        if self.ronda_actual is None: #Es la primera ronda
            self.letras_jugadas = []
        else:
            # Agregar la letra de la ronda anterior al historial de la partida
            if self.ronda_actual.letra_ronda not in self.letras_jugadas:
                self.letras_jugadas.append(self.ronda_actual.letra_ronda)
        
        self.nro_ronda_actual+= 1
        self.ronda_actual = Ronda(
            nro_ronda=self.nro_ronda_actual, categorias=self.categorias,
            jugadores=self.jugadores, letras_jugadas=self.letras_jugadas.copy()
        )
        print(f"A la nueva ronda se le mandó las letras jugadas {self.letras_jugadas}")
        print(f"La nueva ronda eligió la letra: {self.ronda_actual.letra_ronda}")

    def get_letras_jugadas(self):
        return self.letras_jugadas


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
            "letras_jugadas": self.letras_jugadas,
            "total_rondas": self.rondas_maximas
        }
        return info
    
    def terminar_partida(self) -> bool:
        self.estado_actual == EstadoJuego.FIN_JUEGO


