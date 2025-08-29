class EstadoJuego:
    def __init__(self):
        self.respuestas = {}

    def agregar_respuesta(self, jugador, respuesta):
        if jugador not in self.respuestas:
            self.respuestas[jugador] = []
        self.respuestas[jugador].append(respuesta)

    def get_estado(self):
        return self.respuestas

