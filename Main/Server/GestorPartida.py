
""" 
    GestorJuego: Conoce cuándo y qué publicar basado en la lógica del juego
    ConexionServidor: Solo sabe cómo enviar mensajes, pero no cuándo ni qué
"""

import json
from Main.Server.Publisher import Publisher
from Main.Server.Partida import Partida
from Main.Common.AbstractGUI import AbstractGUI
from Main.Server.ConexionServidor import ConexionServidor
import Pyro5.api


# funciones auxiliares 

def dict_to_json(info: dict) -> str:
    try:
        return json.dumps(info, indent=4, ensure_ascii=False)
    except TypeError as e:
        raise ValueError(f"No se pudo convertir a JSON: {e}")


class GestorPartida:
    def __init__(self, gui: AbstractGUI, publisher=None):
        self.Publisher = publisher or Publisher()
        self.Partida = Partida()
        self.Gui = gui
        self.jugadores_requeridos = 4
        
        gui.show_message("[Servidor Lógico] Objeto Gestor Partida Inicializado.")

    def iniciar_partida(self):
        pass

    def finalizar_partida(self):
        pass

    def nickname_disponible(self, nickname: str) -> bool | str:
        is_not_string = not isinstance(nickname, str)
        if (nickname == "" or is_not_string):
            return "Error: NickName vacio o no es cadena!"
        
        formated_nickname = nickname.lower().replace(" ", "")
        existe_jugador = self.Publisher.buscar_jugador(formated_nickname)
        
        if existe_jugador is None:
            return True
        return False

    def unirse_a_sala(self, nickname: str, nombre_logico_jugador: str):
        existe_jugador = self.Publisher.buscar_jugador(nickname)
        if existe_jugador is not None:
            self.Gui.show_error(f"[unirse_sala] Jugador {nickname} ya existe en sala!")
            return f"[Error]: El Jugador {nickname} ya esta en la sala!"

        self.Publisher.suscribirJugador(nickname, nombre_logico_jugador)
        info_sala: dict = self.Partida.get_info_sala(self.Publisher.getJugadores())
        self.Publisher.notificar_info_sala(info_sala)

        self._verificar_jugadores_suficientes()

    def salir_de_sala(self, nickname: str):
        result = self.Publisher.desuscribirJugador(nickname)
        if result is None:
            self.Gui.show_error(f"[salir_de_sala] Jugador {nickname} no existe en la sala")
            return None

    def _verificar_jugadores_suficientes(self):
        cant_jugadores_actual = len(self.Publisher.getJugadoresConfirmados())
        if(cant_jugadores_actual >= self.jugadores_requeridos):
            self.iniciar_partida()

    def confirmar_jugador(self, nickname: str):
        if(not self.Publisher.jugador_esta_suscripto(nickname)):
            self.Gui.show_error(f"Jugador '{nickname}' no esta suscripto o registrado!")
            return

        result = self.Publisher.confirmar_jugador(nickname)
        if(result is None):
            self.Gui.show_error(f"Jugador {nickname} ya ha sido confirmado!")
            return

        msg = {
            "msg": f"Jugador: '{nickname}' Confirmado. Espere a que inicie la ronda."
        }
        self.Publisher.notificar_confirmacion_jugador(nickname=nickname, msg_dict=msg)
