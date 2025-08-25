from utilidades import EstadoJuego

class TuttiFrutti:
    def __init__(self):
        self.estado = EstadoJuego()
        self.clientes = []

    def iniciarJuego(self, nombre_Jugador):
        self.clientes.append(nombre_Jugador)
        return f"{nombre_Jugador} se ha unido al juego."

    def cargar_respuesta(self, nombre_Jugador, respuesta):
        self.estado.agregar_respuesta(nombre_Jugador, respuesta)
        return "Respuesta recibida."

    def get_state(self):
        return self.estado.get_state()