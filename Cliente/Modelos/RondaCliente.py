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
        return {
            "nickname": self.nickname_jugador,
            "categorias": self.categorias_ronda,
            "respuestas": {
                resp.categoria_respuesta: resp.respuesta_texto for resp in self.respuestas
            }
        }


    def agregarRespuesta(self, respuesta):
        self.respuestas.append(respuesta)
    
    