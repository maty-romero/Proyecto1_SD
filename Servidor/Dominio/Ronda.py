from Main.Server.Jugador import Jugador


class Ronda:
    def __init__(self, categorias: list[str], jugadores: list[Jugador], nro_ronda: int):
        self.nro_ronda = nro_ronda
        self.finalizada: bool = False
        self.letra_ronda = "" # self.getLetraRandom()
        self.categorias = categorias
        self.jugadores_ronda = jugadores

    # PENDIENTE --> Completar Clase RONDA y Clase Respuesta

    #letras = list(string.ascii_uppercase)  # ['A', 'B', ..., 'Z']
    """
    def get_letra_random(self) -> str:
        if not self.letras:
            raise ValueError("No quedan letras disponibles")

        letra = random.choice(self.letras)
        self.letras.remove(letra)  # Evita repetir
        self.letras_jugadas.append(letra)
        return letra

        # Lógica de la ronda

    def iniciar_partida(self):
        self.rondaActual = 1
        letra = self.get_letra_random()

    """