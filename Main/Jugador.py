class Jugador:
    def __init__(self, nick):
        self.nickname = nick
        self.puntaje_total = 0

    def sumar_puntaje(self, puntaje):
        self.puntaje_total + puntaje

    def get_puntaje(self):
        return self.puntaje_total

    def get_nickname(self):
        return self.nickname.upper()
