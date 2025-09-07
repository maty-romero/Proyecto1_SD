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


@Pyro5.api.expose
class GestorPartidaService:
    def __init__(self, gui: AbstractGUI):
        self.publisher = Publisher()
        self.partida = Partida()
        self.gui = gui
        self.jugadores_requeridos = 4 # pasar por constructor?
        gui.show_message("[Servidor Lógico] Objeto Gestor Partida Inicializado.")

    def iniciar_partida(self):
        pass

    def finalizar_partida(self):
        pass

    def CheckNickNameIsUnique(self, nickname: str) -> bool | str:
        is_not_string = not isinstance(nickname, str)
        if (nickname == "" or is_not_string):
            return "Error: NickName vacio o no es cadena!"
        formated_nickname = nickname.lower().replace(" ", "")
        existe_jugador = self.publisher.buscar_jugador(formated_nickname)
        if existe_jugador is None: # no existe jugador usando ese nickname
            return True
        return False # nickname no disponible

    def unirse_a_sala(self, nickname: str, nombre_logico_jugador: str):
        # verificar si ya existe jugador en sala
        existe_jugador = self.publisher.buscar_jugador(nickname)
        if existe_jugador is not None:  # jugador ya registrado
            self.gui.show_error("[unirse_sala] Jugador {nickname} ya existe en sala!")
            return f"[Error]: El Jugador {nickname} ya esta en la sala!"

        self.publisher.suscribirJugador(nickname, nombre_logico_jugador)
        info_sala: dict = self.partida.get_info_sala(self.publisher.getJugadores())
        self.publisher.notificar_info_sala(info_sala) # broadcasting

        # ** Thread.sleep? con cronometro para mostrar que va a empezar partida?
        self._verificar_jugadores_suficientes() # Si los hay inicia partida

    def salir_de_sala(self, nickname: str):
        result = self.publisher.desuscribirJugador(nickname)
        if result is None:
            self.gui.show_error("[salir_de_sala] Jugador {nickname} no existe en la sala")
            return None

    def _verificar_jugadores_suficientes(self):
        cant_jugadores_actual = len(self.publisher.getJugadoresConfirmados())
        if(cant_jugadores_actual >= self.jugadores_requeridos):
            self.iniciar_partida()

    def confirmar_jugador(self, nickname: str):
        if(not self.publisher.jugador_esta_suscripto(nickname)):
            self.gui.show_error(f"Jugador '{nickname}' no esta suscripto o registrado. Debe Registrarse primero!")

        result = self.publisher.confirmar_jugador(nickname)
        if(result is None):
            self.gui.show_error(f"Jugador {nickname} ya ha sido confirmado!")

        msg = {
            "msg": f"Jugador: '{nickname}' Confirmado. Espere a que inicie la ronda."
        }
        self.publisher.notificar_confirmacion_jugador(nickname=nickname, msg_dict=msg)
