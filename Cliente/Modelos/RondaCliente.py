from Cliente.Modelos.Respuesta import Respuesta


class RondaCliente:
    def __init__(self, categorias_inicial: list[str], nickname: str):
        self.nickname_jugador = nickname
        self.categorias_ronda = categorias_inicial
        self.respuestas: list[Respuesta] = []

    """
        Utilidad de esta clase: 
        - Logica y Jugabilidad para la ronda
        - Por cada ronda se Instancia en GestorCliente
    """

    # retorna la informacion de la ronda (respuestas de ese jugador
    # en la ronda que se esta jugando) - respuestas en memoria en cliente
    def getRespuestasJugador(self) -> dict:
        pass