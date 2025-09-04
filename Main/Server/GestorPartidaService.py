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
        info_sala: dict = self.partida.get_info_sala()
        self.publisher.notificar_info_sala(info_sala) # broadcasting

        # ** Thread.sleep? con cronometro para mostrar que va a empezar partida?
        self._verificar_jugadores_suficientes() # Si los hay inicia partida

    def salir_de_sala(self, nickname: str):
        result = self.publisher.desuscribirJugador(nickname)
        if result is None:
            self.gui.show_error("[salir_de_sala] Jugador {nickname} no existe en la sala")
            return None
    def _verificar_jugadores_suficientes(self):
        cant_jugadores_actual = len(self.publisher.getJugadores())
        if(cant_jugadores_actual >= self.jugadores_requeridos):
            self.iniciar_partida()
"""
    # PENDIENTE - INICIAR_PARTIDA / COMENZAR_RONDA_1
    def confirmar_jugador(self): # args: nickname ?? 
        inicio_partida: bool = self.partida.confirmar_jugador_partida()
        if(inicio_partida):
            # INICIAR_PARTIDA / JUGAR_RONDA
            info_partida = dict_to_json(self.partida.get_info_ronda())
            for nickname, _ in self.partida.get_jugadores_partida().items():
                self.enviar_info_ronda(nickname, info_partida)
            return {"status": "ok", "accion": "broadcast_info_ronda"}
        return {"status": "esperando más jugadores"}

            # Simulacion para 1 jugador --> [Uso en Cliente] (Enviar info Ronda)
            #jugador = self.partida.get_jugador_partida(nickname)
            # mensaje = self.partida.get_info_ronda()
            # mensaje_json = dict_to_json(mensaje)
            # return mensaje_json
            #self.enviar_info_ronda()

    # Pendiente - DEBERIA SER UN BROADCASTING 
    def enviar_info_ronda(self, nickname: str, mensaje: str):
        self.gui.show_message("*** Server envia mensaje a Cliente ***")
        try:
            nombre_logico_jugador = self.partida.get_jugador_partida(nickname)
            jugador_remoto = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico_jugador}")
            jugador_remoto.recibir_info_ronda(mensaje)
        # if(jugador_remoto is None):
        #     self.gui.show_error(f"El Jugador {nickname} no esta en la partida!")

        except Exception as e:
            self.gui.show_error(f"No se pudo enviar info a {nickname}: {e}")


    # PENDIENTE- Patron strategy o command para mandar info ?? 

    def enviar_info_sala(self, nickname: str, mensaje: str):
        self.gui.show_message("*** Server envia mennsaje a Cliente ***")
        # jugador_remoto = self.partida.get_jugador_partida(nickname)
        nombre_logico_jugador = self.partida.get_jugador_partida(nickname)
        jugador_remoto = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico_jugador}")
        self.gui.show_error(f"enviar_info_sala => jugador: {jugador_remoto}")
        if(jugador_remoto is None):
            self.gui.show_error(f"El Jugador {nickname} no esta en la partida!")
        else:
            jugador_remoto.recibir_info_sala(mensaje)

    # "Equivalente a => registrar_cliente"
    def unirse_a_sala(self, nickname: str, nombre_logico_jugador: str):
        proxy_cliente = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico_jugador}")
        print(f"UNIRSE A SALA | PROXY_CLIENTE: {proxy_cliente}")
        self.gui.show_message(f"Registrando jugador: {nickname}, con nombre_logico: {nombre_logico_jugador}")

        result = self.partida.agregar_jugador_partida(nickname, nombre_logico_jugador) # se agrega nombre logico
        if(result is None):
            self.gui.show_error(f"El jugador {nickname} ya ha sido registrado")

        # devolver json info para la sala
        info_sala_json = dict_to_json(self.partida.get_info_sala())

        # prueba - borrar consola cliente e imprimir json info sala
        self.enviar_info_sala(nickname, info_sala_json)
        

    

    # def Funcion para enviar desde cliente a servidor las respuestas del jugador ganador
"""