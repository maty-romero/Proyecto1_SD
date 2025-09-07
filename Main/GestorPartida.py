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

            # info_partida = dict_to_json(self.partida.get_info_ronda())
            # for nickname, _ in self.partida.get_jugadores_partida().items():
            #     self.enviar_info_ronda(nickname, info_partida)

            #simula una ronda ya finalizada
            self.iniciar_votacion_ronda()
            return {"status": "ok", "accion": "broadcast_info_ronda"}
        return {"status": "esperando más jugadores"}


    def enviar_info_ronda(self, nickname: str, mensaje: str):
        self.gui.show_message("*** Server envia mensaje a Cliente ***")
        try:
            nombre_logico_jugador = self.partida.get_jugador_partida(nickname)
            jugador_remoto = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico_jugador}")
            jugador_remoto.recibir_info_ronda(mensaje)
            if(jugador_remoto is None):
                self.gui.show_error(f"El Jugador {nickname} no esta en la partida!")

        except Exception as e:
            self.gui.show_error(f"No se pudo enviar info a {nickname}: {e}")


    # PENDIENTE- Patron strategy o command para mandar info ?? 

    def enviar_info_sala(self, nickname: str, mensaje: str):
        self.gui.show_message("*** Server envia mensaje a Cliente ***")
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
        

    def CheckNickNameIsUnique(self, nickname: str):
        is_not_string = not isinstance(nickname, str)
        if (nickname == "" or is_not_string):
            return "Error: NickName vacio o no es cadena!"

        formated_nickname = nickname.lower().replace(" ", "")
        is_unique: bool = self.partida.is_nickname_disponible(formated_nickname)
        return is_unique

    # def Funcion para enviar desde cliente a servidor las respuestas del jugador ganador


    def iniciar_votacion_ronda(self):
        self.enviar_respuestas_ronda()
        self.enviar_resultados_votacion()


    def enviar_respuestas_ronda(self):
        ronda = self.partida.rondas[-1]  # última ronda
        mensaje_json = json.dumps(ronda.to_dict(), indent=4, ensure_ascii=False)

        # enviar a todos los clientes
        for nickname in self.partida.get_jugadores_partida().keys():
            self.enviar_info_ronda(nickname, mensaje_json)


    def registrar_votos(self, votos_data: dict):
        try:
            votos = votos_data["votos"]
            ronda = self.partida.rondas[-1]
            for jugador_responde, categorias in votos.items():
                for categoria, voto in categorias.items():
                    respuesta = ronda.get_respuestas()[jugador_responde][categoria]
                    respuesta.registrar_voto(voto)

            #calcula validez de todas las respuestas
            for jugador_responde, categorias in ronda.get_respuestas().items():
                for categoria, resp in categorias.items():
                    resp.contar_votos()

            return {"status": "ok", "detalle": f"Votos registrados"}
        except Exception as e:
            return {"status": "error", "detalle": str(e)}


    def enviar_resultados_votacion(self):
        try:
            # Prepara resumen de respuestas y validez
            ronda = self.partida.rondas[-1]
            respuestas = ronda.get_respuestas()
            resumen = {}

            for nickname, categorias in respuestas.items():
                resumen[nickname] = {}
                for categoria, respuesta_obj in categorias.items():
                    resumen[nickname][categoria] = {
                        "respuesta": str(respuesta_obj.respuesta),
                        "valida": respuesta_obj.valido if hasattr(respuesta_obj, "valido") else None,
                        "votos": respuesta_obj.votos if hasattr(respuesta_obj, "votos") else None
                    }

            mensaje_json = dict_to_json(resumen)

            # Enviar resumen a todos los clientes
            for nickname, _ in self.partida.get_jugadores_partida().items():
                self.enviar_info_ronda(nickname, mensaje_json)

            return {"status": "ok", "detalle": "Ronda finalizada y resumen enviado"}
        except Exception as e:
            return {"status": "error", "detalle": str(e)}




