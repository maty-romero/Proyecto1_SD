class Respuesta:
    def __init__(self, categoria: str):
        self.categoria_respuesta = categoria
        self.respuesta_texto = "" # lo que responda el cliente
        self.validez: bool
        self.puntaje_asignado: int = 0

