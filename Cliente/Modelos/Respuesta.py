class Respuesta:
    def __init__(self, categoria: str, respuesta: str):
        self.categoria_respuesta = categoria
        self.respuesta_texto = respuesta # lo que responda el cliente
        self.validez: bool
        self.puntaje_asignado: int = 0


    def to_dict(self):
        return {
            "categoria": self.categoria_respuesta,
            "respuesta": self.respuesta_texto
            #"validez": self.validez
        }