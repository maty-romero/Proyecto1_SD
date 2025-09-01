import random
import string

class Partida:
    def __init__(self):
        self.jugadores = {} # { "<nickname>" : objeto_remoto_cliente }
        self.categorias = ["Nombres", "Paises o ciudades", "Objetos"]
        self.rondas = 3 # nro rondas
        self.rondaActual = 0; 
        self.letras = list(string.ascii_uppercase)  # ['A', 'B', ..., 'Z']
        self.letras_jugadas = [] 
        self.jugadores_confirmados = 0

    def is_nickname_disponible(self, nickname: str):
        if nickname in self.jugadores:
            return False
        return True

    def agregar_jugador_partida(self, nickname: str, objeto_cliente_remoto):
        if(nickname in self.jugadores):
            return None # jugador ya registrado
        self.jugadores[nickname] = objeto_cliente_remoto 
            
    def eliminar_jugador_partida(self, nickname: str):
        if(not(nickname in self.jugadores)):
            return None 
        self.jugadores.pop(nickname) # existe jugador
        
    def get_jugador_partida(self, nickname: str):
        if(not(nickname in self.jugadores)):
            return None # no existe jugador
        return self.jugadores[nickname]

    def get_letras_jugadas(self):
        return self.letras_jugadas

    def get_letra_random(self) -> str:
        if not self.letras:
            raise ValueError("No quedan letras disponibles")
        
        letra = random.choice(self.letras)
        self.letras.remove(letra)  # Evita repetir
        self.letras_jugadas.append(letra)
        return letra

    # GETS INFO

    def get_info_sala(self):
        info = {
            "categorias": self.categorias,
            "jugadores": list(self.jugadores.keys()),
            "rondas": self.rondas
        }
        return info;  

    # PENDIENTE - NroRondaActual 
    def get_info_ronda(self):
        info = {
            "categorias": self.categorias,
            "nro_ronda": -1,  
            "letra_ronda": 'pendiente',
            "letras_jugadas": 'pendiente'
        }
        return info
    
     # PENDIENTE - Definir bien
    def confirmar_jugador_partida(self) -> bool:
        # self.jugadores_confirmados+= 1
        # return self.jugadores_confirmados == 3 
        return True
    
    #     def iniciarJuego(self, nombre_Jugador):
    #         self.clientes.append(nombre_Jugador)
    #         return f"{nombre_Jugador} se ha unido al juego."

    



