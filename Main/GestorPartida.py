import json
from Partida import Partida
from AbstractGUI import AbstractGUI
import Pyro5.api

# funciones auxiliares 

def dict_to_json(info: dict) -> str:
    try:
        return json.dumps(info, indent=4, ensure_ascii=False)
    except TypeError as e:
        raise ValueError(f"No se pudo convertir a JSON: {e}")


@Pyro5.api.expose
class GestorPartida:
    def __init__(self, gui: AbstractGUI):
        self.partida = Partida() # jugadores, categorias y nro ronda
        self.gui = gui
        gui.show_message("[Servidor Lógico] Objeto Gestor Partida Inicializado.")

    # PENDIENTE - INICIAR_PARTIDA / COMENZAR_RONDA_1
    def confirmar_jugador(self): # args: nickname ?? 
        inicio_partida: bool = self.partida.confirmar_jugador_partida()
        if(inicio_partida):
            # INICIAR_PARTIDA / JUGAR_RONDA

            # Simulacion para 1 jugador --> [Uso en Cliente] (Enviar info Ronda)
            #jugador = self.partida.get_jugador_partida(nickname)
            mensaje = self.partida.get_info_ronda()
            mensaje_json = dict_to_json(mensaje)
            return mensaje_json
            #self.enviar_info_ronda()


    # Pendiente - DEBERIA SER UN BROADCASTING 
    def enviar_info_ronda(self, nickname: str, mensaje: str):
        self.gui.show_message("*** Server envia mennsaje a Cliente ***")
        jugador_remoto = self.partida.get_jugador_partida(nickname)
        if(jugador_remoto is None):
            self.gui.show_error(f"El Jugador {nickname} no esta en la partida!")
        
        jugador_remoto.recibir_info_ronda(mensaje) 

    # PENDIENTE- Patron strategy o command para mandar info ?? 

    def enviar_info_sala(self, nickname: str, mensaje: str):
        self.gui.show_message("*** Server envia mennsaje a Cliente ***")
        jugador_remoto = self.partida.get_jugador_partida(nickname)
        self.gui.show_error(f"enviar_info_sala => jugador: {jugador_remoto}")
        if(jugador_remoto is None):
            self.gui.show_error(f"El Jugador {nickname} no esta en la partida!")
        else:
            jugador_remoto.recibir_info_sala(mensaje)

    # "Equivalente a => registrar_cliente"
    def unirse_a_sala(self, nickname: str, nombre_logico_jugador: str):
        proxy_cliente = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico_jugador}")
        print(f"UNIRSE A SALA | PROXI_CLIENTE: {proxy_cliente}")
        self.gui.show_message(f"Registrando jugador: {nickname}, con nombre_logico: {nombre_logico_jugador}")

        result = self.partida.agregar_jugador_partida(nickname, proxy_cliente) # se agrega objeto remoto
        if(result is None):
            self.gui.show_error(f"El jugador {nickname} ya ha sido registrado")

        # devolver json info para la sala
        info_sala_json = dict_to_json(self.partida.get_info_sala())

        # prueba - borrar consola cliente e imprimir json info sala
        self.enviar_info_sala(nickname, info_sala_json)
        

    def CheckNickNameIsUnique(self, nickname: str):
        is_not_string = not isinstance(nickname, str)
        if (nickname == "" or is_not_string):
            return "Error: NickName vacio o no es cadena!"

        formated_nickname = nickname.lower().strip(' ')
        is_unique: bool = self.partida.is_nickname_disponible(formated_nickname)
        return is_unique

    # def Funcion para enviar desde cliente a servidor las respuestas del jugador ganador
  