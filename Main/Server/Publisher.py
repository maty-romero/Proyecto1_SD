import Pyro5
import json

from Main.Server.Jugador import Jugador


class Publisher:
    def __init__(self):
        self.jugadores: list[Jugador] = [] # List<Jugador>
        self.jugadores_confirmados = list[Jugador] = []

    def suscribirJugador(self, nickname, nombre_logico):
        jugador = Jugador(nickname, nombre_logico)
        self.jugadores.append(jugador)

    def desuscribirJugador(self, nickname):
        jugador = self._buscar_jugador(nickname)
        if(Jugador is None):
            return None # no existe jugador con ese nickname
        self.jugadores.remove(jugador)

    def getJugadores(self):
        return self.jugadores

    def buscar_jugador(self, nickname: str) -> Jugador | None:
        for jugador in self.jugadores:
            if jugador.nickname == nickname:
                return jugador
        return None # no existe jugador

    def confirmar_jugador(self) -> Jugador | None:
        pass

    # Notificaciones a Clientes

    def notificar_info_sala(self, msg_dict: dict):
        # json = self._dict_to_json(msg_dict)
        pass

    def notificar_inicio_ronda(self, msg_dict: dict):
        pass

    def notificar_fin_ronda(self, msg_dict: dict): # resultado de la ronda
        pass

    def notificar_inicio_votacion(self, msg_dict: dict):
        pass

    def notificar_resultado_partida(self, msg_dict: dict):
        pass

    # Metodos 'Privados'

    def _get_proxy_jugador(self, nickname: str):
        jugador = self._buscar_jugador(nickname)
        if jugador is not None:
            proxy_cliente = Pyro5.api.Proxy(f"PYRONAME:{jugador.nombre_logico}")
            return proxy_cliente

    def _dict_to_json(info: dict) -> str:
        try:
            return json.dumps(info, indent=4, ensure_ascii=False)
        except TypeError as e:
            raise ValueError(f"No se pudo convertir a JSON: {e}")