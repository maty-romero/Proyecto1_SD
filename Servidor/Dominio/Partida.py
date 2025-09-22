
from Servidor.Dominio.Jugador import Jugador
from Servidor.Dominio.Ronda import Ronda

class Partida:
    def __init__(self):
        self.categorias = ["Nombres","Animal","Color","Paises o ciudades","Objetos"]
        self.rondas_maximas = 3  # mandar por constructor?
        self.rondas = [] 
        self.rondaActual = 0
        self.letras = list(string.ascii_uppercase)  # ['A', 'B', ..., 'Z']
        self.rondas_stack: list[Ronda] = []  # Pendiente - Actua como pila
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

    def iniciar_nueva_ronda(self):
        self.nro_ronda_actual+= 1
        self.ronda_actual = Ronda(
            nro_ronda=self.nro_ronda_actual, categorias=self.categorias,
            jugadores=self.jugadores, letras_jugadas=self.letras_jugadas
        )

    def get_letras_jugadas(self) -> list[str]:
        pass  # Recorrer Rondas y armar listas con letras jugadas

    def get_jugadores_partida(self):
        return self.jugadores   # Retorna la lista de jugadores en la partida

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








