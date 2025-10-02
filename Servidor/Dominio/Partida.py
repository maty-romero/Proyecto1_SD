
from enum import Enum, auto
from Servidor.Dominio.Jugador import Jugador
from Servidor.Dominio.Ronda import Ronda

"""----------Clase Estatica estados-----------------------------------------------------------------------------------------------------------"""
class EstadoJuego(Enum):
    #Estados fuera de la ronda
    EN_SALA = auto()
    MOSTRANDO_RESULTADOS_FINALES = auto()

    #Estados dentro de la ronda
    RONDA_EN_CURSO = auto()
    EN_VOTACIONES = auto()
"""---------------------------------------------------------------------------------------------------------------------"""

class Partida:
    def __init__(self):
        self.crear_nueva_partida()

    def crear_nueva_partida (self):
        self.categorias = ["Nombres", "Animales", "Colores" ,"Paises o ciudades", "Objetos"]
        self.rondas_maximas = 1
        self.nro_ronda_actual = 0
        self.letras_jugadas: list[str] = []
        self.ronda_actual: Ronda = None
        self.jugadores: list[Jugador] = []
        self.estado_actual = EstadoJuego.EN_SALA
        self.iniciar_nueva_ronda()
        
    def get_estado_actual(self):
        return self.estado_actual
        
    def set_estado_actual(self,estado_actual):
        self.estado_actual=estado_actual

    def eliminar_jugador_partida(self, nickname: str):
        for jugador in self.jugadores:
            if jugador.nickname == nickname: 
                self.jugadores.remove(jugador)

    # Se asume que hay jugadores requeridos para jugar
    def cargar_jugadores_partida(self, jugadores: list[Jugador]):
        self.jugadores = jugadores

    def calcular_puntos_partida(self):
        puntajes_totales = {}
        for jugador in self.jugadores:
            puntajes_totales[jugador.nickname] = jugador.get_puntaje()

        puntaje_maximo = max(jugador.get_puntaje() for jugador in self.jugadores)
        ganadores = [jugador for jugador in self.jugadores if jugador.get_puntaje() == puntaje_maximo]

        if len(ganadores) == 1:
            ganador = ganadores[0].nickname
        else:
            ganador = f"Empate entre: {', '.join([g.nickname for g in ganadores])}"

        return puntajes_totales, ganador

    def iniciar_nueva_ronda(self):
        if self.ronda_actual is None: #Es la primera ronda
            self.letras_jugadas = []
        else:
            # Agregar la letra de la ronda anterior al historial de la partida
            if self.ronda_actual.letra_ronda not in self.letras_jugadas:
                self.letras_jugadas.append(self.ronda_actual.letra_ronda)
        
        self.nro_ronda_actual+= 1
        self.ronda_actual = Ronda(
            nro_ronda=self.nro_ronda_actual, categorias=self.categorias,
            jugadores=self.jugadores, letras_jugadas=self.letras_jugadas.copy()
        )
        print(f"A la nueva ronda se le mandó las letras jugadas {self.letras_jugadas}")
        print(f"La nueva ronda eligió la letra: {self.ronda_actual.letra_ronda}")

    def get_letras_jugadas(self):
        return self.letras_jugadas


    def get_jugadores_partida(self):
        return self.jugadores

    def eliminar_jugador_partida(self, nickname: str):
        self.jugadores.pop(nickname) # Desconexion o fallo del cliente ?
        pass

    # GETS INFO
    def get_info_sala(self) -> dict:
        info = {
            "categorias": self.categorias,
            "rondas": self.rondas_maximas
        }
        return info

    def get_info_ronda(self):
        info = {
            "categorias": self.categorias,
            "nro_ronda": self.nro_ronda_actual,
            "letra_ronda": self.ronda_actual.letra_ronda,
            "letras_jugadas": self.letras_jugadas,
            "total_rondas": self.rondas_maximas
        }
        return info
    
    def terminar_partida(self) -> bool:
        self.estado_actual == EstadoJuego.FIN_JUEGO

    @staticmethod
    def reconstruir_datos_partida(datos_partida: dict):
        """Restaura una partida desde los datos de la base de datos"""
        partida = Partida()
        
        # Restaurar datos básicos
        partida.categorias = datos_partida.get("categorias", partida.categorias)
        partida.nro_ronda_actual = datos_partida.get("nro_ronda", 0)
        partida.letras_jugadas = datos_partida.get("letras_jugadas", [])
        
        # Restaurar jugadores
        clientes_conectados = datos_partida.get("clientes_Conectados", [])
        partida.jugadores = [Jugador.reconstruir_datos_jugador(cliente) for cliente in clientes_conectados]
        
        # Restaurar ronda actual si existe
        if partida.nro_ronda_actual > 0:
            letra_actual = datos_partida.get("letra", "")
            respuestas = datos_partida.get("respuestas", {})
            
            partida.ronda_actual = Ronda.reconstruir_datos_ronda({
                "nro_ronda": partida.nro_ronda_actual,
                "categorias": partida.categorias,
                "letra": letra_actual,
                "respuestas": respuestas
            }, partida.jugadores, partida.letras_jugadas)
        
        # Restaurar estado desde BD o determinar por lógica
        estado_bd = datos_partida.get("estado_actual")
        if estado_bd:
            # Convertir string a Enum: "EN_SALA" -> EstadoJuego.EN_SALA
            try:
                partida.estado_actual = EstadoJuego[estado_bd]
            except KeyError:
                # Si el estado en BD no es válido, usar lógica por defecto
                partida.estado_actual = EstadoJuego.RONDA_EN_CURSO if partida.nro_ronda_actual > 0 else EstadoJuego.EN_SALA
        else:
            # Si no hay estado en BD, determinar por lógica
            partida.estado_actual = EstadoJuego.RONDA_EN_CURSO if partida.nro_ronda_actual > 0 else EstadoJuego.EN_SALA
            
        return partida









