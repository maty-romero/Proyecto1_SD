from abc import ABC, abstractmethod

class PuntajeStrategy(ABC):
    @abstractmethod
    def calcular_puntaje(self, respuestas):
        pass

class PuntajeSimple(PuntajeStrategy):
    """Cada respuesta correcta suma 10 puntos."""
    def calcular_puntaje(self, respuestas):
        return {jugador: len(resps)*10 for jugador, resps in respuestas.items()}

class PuntajeAvanzado(PuntajeStrategy):
    """Ejemplo: puntaje basado en votaciones (1 punto por voto recibido)."""
    def calcular_puntaje(self, respuestas):
        # Para demo asignamos random puntos
        import random
        return {jugador: sum(random.randint(0,5) for _ in resps) for jugador, resps in respuestas.items()}
