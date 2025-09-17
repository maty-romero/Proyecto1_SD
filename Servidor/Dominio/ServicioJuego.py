
import Pyro5.api

from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Dominio.Partida import Partida
from Servidor.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Utils.SerializeHelper import SerializeHelper


@Pyro5.api.expose
class ServicioJuego:
    def __init__(self, dispacher: Dispatcher):
        self.dispacher = dispacher
        self.partida = Partida()
        self.logger = ConsoleLogger(name="ServicioJuego", level="INFO") # cambiar si se necesita 'DEBUG'
        self.jugadores_requeridos = 4 # pasar por constructor?
        self.logger.info("Servicio Juego inicializado")

    """
        ServicioJuego --> Entran las llamadas Pyro
    
        Servicios Registrados en NodoServidor --> Dispacher
            - "comunicacion"
            - "db"
        Ejemplo de uso Dispacher: 
            self.Dispatcher.manejar_llamada("comunicacion", "broadcast", "¡Hola a todos!")
        Ejemplo de uso SerializeHelper:
            json = SerializeHelper.serializar(exito=False, msg="", datos={"datos"})
        
    """
    """
    def iniciar_partida(self):
        # Comenzar Ronda y avisar a todos etc.
        pass

    def finalizar_partida(self):
        # notificar y enviar info fin_partida
        pass
    """

    # PENDIENTE - Manejar intentos de unirse o acceso en otros estados de la partida
    def solicitar_acceso(self):
        hay_lugar: bool = self.dispacher.manejar_llamada(
            "comunicacion", # nombre_servicio
            "hay_lugar_disponible", # nombre_metodo
             self.jugadores_requeridos # args
        )

        if not hay_lugar:
            return SerializeHelper.serializar(exito=False, msg="La sala esta llena, no puede unirse!")
        # hay lugar
        return SerializeHelper.serializar(exito=False, msg="Hay lugar disponible, puede unirse!")

    def CheckNickNameIsUnique(self, nickname: str):
        is_not_string = not isinstance(nickname, str)

        if (nickname == "" or is_not_string):
            return SerializeHelper.serializar(exito=False, msg="NickName vacio o no tiene formato valido")

        formated_nickname = nickname.lower().replace(" ", "")

        existe_jugador = self.publisher.buscar_jugador(formated_nickname)
        if existe_jugador is None: # no existe jugador usando ese nickname
            result = RespuestaRemotaJSON(
                exito=True, mensaje="NickName disponible")
            return result.serializar()

        # nickname no disponible
        result = RespuestaRemotaJSON(
            exito=False, mensaje="El nickname ya esta siendo utilizado")
        return result.serializar()

    def unirse_a_sala(self, nickname: str, nombre_logico_jugador: str):
        # verificar si ya existe jugador en sala
        existe_jugador = self.publisher.buscar_jugador(nickname)
        """
        if existe_jugador is not None:  # jugador ya registrado
            self.gui.show_error("[unirse_sala] Jugador {nickname} ya existe en sala!")
            result = RespuestaRemotaJSON(
                exito=False, mensaje="El Jugador {nickname} ya esta en la sala!")
            return result.serializar() # json

            return f"[Error]: El Jugador {nickname} ya esta en la sala!"
        """
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
