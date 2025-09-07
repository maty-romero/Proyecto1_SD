import Pyro5
import json

from Main.Server.Jugador import Jugador


class Publisher:
    def __init__(self):
        self.jugadores: list[Jugador] = [] # List<Jugador>
        self.nicknames_confirmados: set[str] = set() # List<nicknames>

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

    def getJugadoresConfirmados(self) -> set():
        return self.nicknames_confirmados

    def confirmar_jugador(self, nickname: str) -> bool | None:
        if (nickname is self.nicknames_confirmados):
            return None  # Jugador ya confirmado
        self.nicknames_confirmados.add(nickname)
        return True

    def jugador_esta_suscripto(self, nickname: str):
        for jugador in self.jugadores:
            if jugador.nickname == nickname:
                return True
        return False # Jugador no suscripto o registrado

    # Notificaciones a Clientes

    def notificar_info_sala(self, msg_dict: dict):
        json = Publisher._dict_to_json(msg_dict)
        for jugador in self.jugadores: # Broadcasting
            self._get_proxy_jugador(jugador.nickname).recibir_info_sala(json)

    def notificar_confirmacion_jugador(self, nickname: str, msg_dict: dict):
        json = Publisher._dict_to_json(msg_dict)
        # notificacion solo a un cliente
        self._get_proxy_jugador(nickname).recibir_info_confirmar_jugador(json)

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
        jugador = self.buscar_jugador(nickname)
        if jugador is not None:
            proxy_cliente = Pyro5.api.Proxy(f"PYRONAME:{jugador.nombre_logico}")
            return proxy_cliente

    def buscar_jugador(self, nickname: str) -> Jugador | None:
        for jugador in self.jugadores:
            if jugador.nickname == nickname:
                return jugador
        return None # no existe jugador

    @staticmethod
    def _dict_to_json(info: dict) -> str:
        try:
            return json.dumps(info, indent=4, ensure_ascii=False)
        except TypeError as e:
            raise ValueError(f"No se pudo convertir a JSON: {e}")