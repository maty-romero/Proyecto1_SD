
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
            return SerializeHelper.respuesta(
                exito=False,
                msg="La sala está llena, no puede unirse."
            )

        # hay lugar
        return SerializeHelper.respuesta(
            exito=True,
            msg="Hay lugar disponible, puede unirse."
        )


    def CheckNickNameIsUnique(self, nickname: str):
        is_not_string = not isinstance(nickname, str)

        if (nickname == "" or is_not_string):
            return SerializeHelper.respuesta(
                exito=False,
                msg="NickName vacio o no tiene formato valido"
            )

        formated_nickname = nickname.lower().replace(" ", "")

        is_nickname_disponible: bool = self.dispacher.manejar_llamada(
            "comunicacion", # nombre_servicio
            "is_nickname_disponible", # nombre_metodo
             formated_nickname # args
        )

        # nickname no disponible
        if not is_nickname_disponible:
            return SerializeHelper.respuesta(
                exito=False,
                msg="El nickname ingresado ya esta siendo utilizado"
            )
        # nickname ingresado esta disponible
        return SerializeHelper.respuesta(exito=True, msg="NickName disponible")

    def unirse_a_sala(self, info_cliente: dict):
        """
        1. Verificar si existe ya jugador en sala ???
        2. Suscribir / Registrar Jugador
        3. Conectarse al socket del Cliente (se hace al suscribir cliente)
        4. Notificar entrada de nuevo a todos los jugadores (broadcast)
        5. Obtener info Sala
        6. Retornar info Sala via Pyro
        """
        #ServicioComunicacion. suscribir_cliente(self, nickname, nombre_logico, ip_cliente, puerto_cliente
        try:
            nickname = info_cliente['nickname']
            nombre_logico = info_cliente['nombre_logico']
            ip_cliente = info_cliente['ip']
            puerto_cliente = info_cliente['puerto']
            self.dispacher.manejar_llamada(
                "comunicacion",  # nombre_servicio
                "suscribir_cliente",  # nombre_metodo
                nickname, nombre_logico, ip_cliente, puerto_cliente  # args
            )

            # PENDIENTE
            # Notificar entrada nuevo jugador - Broadcast Socket

            # obtener info sala
            nicknames_jugadores: list[str] = self.dispacher.manejar_llamada(
                "comunicacion",  # nombre_servicio
                "listado_nicknames",  # nombre_metodo
            )

            info_sala: dict = self.partida.get_info_sala()
            info_sala['jugadores'] = nicknames_jugadores
            # retorna infor de sala a quien se unió
            return SerializeHelper.respuesta(
                exito=True,
                msg="Se ha unido a la sala exitosamente",
                datos=info_sala
            )
            # PENDIENTE
            # self._verificar_jugadores_suficientes()  # Si los hay inicia partida

        except Exception as e:  # Catches any other exception
            self.logger.error(f"Ocurrio un error al unirse a la sala: {e}")



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
