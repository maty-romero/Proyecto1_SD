class Jugador:
    def __init__(self, nickname: str):
        self.nickname = nickname
        self.confirmado: bool = False
        self.puntaje_total = 0

    def set_confirmar(self):
        self.confirmado=True

    def reset_confirmar(self):
        self.confirmado=False

    def get_confirmacion(self):
        return self.confirmado

    def sumar_puntaje(self, puntos: int):
        if(not (puntos < 0)):
            self.puntaje_total += puntos

    def get_puntaje(self) -> int:
        return self.puntaje_total
    
    @staticmethod
    def desde_datos_bd(datos_cliente: dict):
        """Crea un objeto Jugador desde los datos de la base de datos"""
        jugador = Jugador(datos_cliente["nickname"])
        # Restaurar puntaje si existe en BD
        jugador.puntaje_total = datos_cliente.get("puntaje_total", 0)
        return jugador
    