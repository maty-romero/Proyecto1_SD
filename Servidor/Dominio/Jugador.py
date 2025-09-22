class Jugador:
    def __init__(self, nickname: str):
        self.nickname = nickname
        self.confirmado: bool = False
        self.puntaje_total = 0

    def sumar_puntaje(self, puntos: int):
        if(not (puntos < 0)):
            self.puntaje_total += puntos

    def get_puntaje(self) -> int:
        return self.puntaje_total