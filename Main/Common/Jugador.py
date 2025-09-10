class Jugador():

    def __init__(self, nickname: str, nombre_logico=None,puntaje=0):
        
        if not nickname or not nickname.strip():  # Valida que no esté vacío después del strip
            raise ValueError("El nickname no puede estar vacío")
        
        self.nickname = nickname  # Mantiene espacios originales
        # Si no se proporciona nombre_logico, lo generamos automáticamente
        # Esto puede cambiar para que se genere automaticamente, tanto en cliente como en servidor
        if nombre_logico is None:
            #el strip garantiza que no va a haber espacios en blanco para la generacion del nombre logico
            self.nombre_logico = f"jugador.{nickname.strip()}"
        else:
            self.nombre_logico = nombre_logico
        
        self.puntaje_total = puntaje

    def get_nickname(self):
        return self.nickname

    def get_nombre_logico(self):
        return self.nombre_logico

    def sumar_puntaje(self, puntos: int):
        if puntos >= 0:
            self.puntaje_total += puntos
        else:
            raise ValueError("Los puntos a sumar no pueden ser negativos.")

    def get_puntaje(self) -> int:
        return self.puntaje_total

    #impresion de datos del jugador por consola
    def __str__(self):
        return f"Jugador {self.nombre} con {self.puntaje} puntos" # Jugador Pepe con 30 puntos

""" 
    Futura implementacion: Clase abstracta de jugador para herencia en JugadorCliente y JugadorServidor

    from typing import Optional
    from abc import ABC, abstractmethod 
    
    class JugadorBase(ABC):
        def __init__(self, nickname: str,puntaje=0):
            if not nickname or not nickname.strip():  # Valida que no esté vacío después del strip
                raise ValueError("El nickname no puede estar vacío")
            
            self.nickname = nickname  # Mantiene espacios originales
            # El strip se hace en cada subclase según necesite
            self.nombre_logico = self._generar_nombre_logico()
            self.puntaje_total = puntaje
        
        @property
        @abstractmethod
        def nombre_logico(self) -> str:
            '''Cada subclase define cómo generar su nombre lógico. Puede quedar como una sola generacion que sea igual en cliente y servidor'''
            pass

    class JugadorCliente(JugadorBase):
        def _generar_nombre_logico(self) -> str:
            return f"jugador.{self.nickname.strip()}"  # Strip aquí
"""