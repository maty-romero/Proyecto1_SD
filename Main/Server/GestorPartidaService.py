import json

from Main.Server.Publisher import Publisher
from Partida import Partida
from Main.Common.AbstractGUI import AbstractGUI
import Pyro5.api

# funciones auxiliares 

def dict_to_json(info: dict) -> str:
    try:
        return json.dumps(info, indent=4, ensure_ascii=False)
    except TypeError as e:
        raise ValueError(f"No se pudo convertir a JSON: {e}")


'''----------------Alternativas estado de juego-----------------------------------------------------------------------------------------------------------------------------------------------------------'''
#1
from enum import Enum
class EstadoJuego(Enum):
    #Estados fuera de la ronda
    ESPERANDO_JUGADORES = 1
    FIN_JUEGO = 2

    #Estados dentro de la ronda
    EN_PREPARACION_RONDA = 3 #tal vez no haga falta
    EN_RONDA = 4
    EN_VOTACION = 5
    MOSTRANDO_RESULTADOS = 6

#2

transiciones = {
    "esperando_jugadores": ["en_ronda"],
    "en_ronda": ["en_votacion"],
    "en_votacion": ["resultados_ronda"],
    "resultados_ronda": ["en_ronda", "resultados_partida"],
    "resultados_partida": ["esperando_jugadores"]
}
    

    # def __init__(self):
    #     self.estado_actual = "esperando_jugadores"

def cambiar_estado(self, nuevo_estado):
    if nuevo_estado in self.transiciones[self.estado_actual]:
        self.estado_actual = nuevo_estado
    else:
        raise ValueError(f"Transición inválida de {self.estado_actual} a {nuevo_estado}")
'''---------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''


@Pyro5.api.expose
class GestorPartidaService:
    # Estados_Juego =EstadoJuego()
    # if self.Partida.estado_actual == self.Estados_Juego.EN_RONDA:
    #     pass
    # estados_Juego = [
    # ["esperando_jugadores", "fin_juego"],      # estados fuera de ronda
    # ["en_preparacion_ronda", "en_ronda", "en_votacion", "mostrando_resultados"]  # estados dentro de ronda
    # ]
    def __init__(self, Gui: AbstractGUI):
        self.Publisher = Publisher()
        self.Partida = Partida()
        self.Gui = Gui
        self.jugadores_requeridos = 4 # pasar por constructor?
        Gui.show_message("[Servidor Lógico] Objeto Gestor Partida Inicializado.")

    def iniciar_partida(self):
        pass

    def finalizar_partida(self):
        pass

    def CheckNickNameIsUnique(self, nickname: str) -> bool | str:
        is_not_string = not isinstance(nickname, str)
        if (nickname == "" or is_not_string):
            return "Error: NickName vacio o no es cadena!"
        formated_nickname = nickname.lower().replace(" ", "")
        existe_jugador = self.Publisher.buscar_jugador(formated_nickname)
        if existe_jugador is None: # no existe jugador usando ese nickname
            return True
        return False # nickname no disponible

    def unirse_a_sala(self, nickname: str, nombre_logico_jugador: str):
        # verificar si ya existe jugador en sala
        existe_jugador = self.Publisher.buscar_jugador(nickname)
        if existe_jugador is not None:  # jugador ya registrado
            self.Gui.show_error("[unirse_sala] Jugador {nickname} ya existe en sala!")
            return f"[Error]: El Jugador {nickname} ya esta en la sala!"

        self.Publisher.suscribirJugador(nickname, nombre_logico_jugador)
        info_sala: dict = self.Partida.get_info_sala(self.Publisher.getJugadores())
        self.Publisher.notificar_info_sala(info_sala) # broadcasting

        # ** Thread.sleep? con cronometro para mostrar que va a empezar partida?
        self._verificar_jugadores_suficientes() # Si los hay inicia partida

    def salir_de_sala(self, nickname: str):
        result = self.Publisher.desuscribirJugador(nickname)
        if result is None:
            self.Gui.show_error("[salir_de_sala] Jugador {nickname} no existe en la sala")
            return None

    def _verificar_jugadores_suficientes(self):
        cant_jugadores_actual = len(self.Publisher.getJugadoresConfirmados())
        if(cant_jugadores_actual >= self.jugadores_requeridos):
            self.iniciar_partida()

    def confirmar_jugador(self, nickname: str):
        if(not self.Publisher.jugador_esta_suscripto(nickname)):
            self.Gui.show_error(f"Jugador '{nickname}' no esta suscripto o registrado. Debe Registrarse primero!")

        result = self.Publisher.confirmar_jugador(nickname)
        if(result is None):
            self.Gui.show_error(f"Jugador {nickname} ya ha sido confirmado!")

        msg = {
            "msg": f"Jugador: '{nickname}' Confirmado. Espere a que inicie la ronda."
        }
        self.Publisher.notificar_confirmacion_jugador(nickname=nickname, msg_dict=msg)
