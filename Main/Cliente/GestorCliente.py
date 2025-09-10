import sys
import threading
import time
import Pyro5

from Main.Cliente.JugadorCliente import JugadorCliente
from Main.Common.AbstractGUI import AbstractGUI
from Main.Utils.ComunicationHelper import ComunicationHelper
from Main.Cliente.ServicioCliente import ServicioCliente
from Main.Utils.RespuestaRemotaJSON import RespuestaRemotaJSON


class GestorCliente:
    def __init__(self, gui: AbstractGUI):
        self.gui = gui
        self.nombre_logico_server = "gestor.partida"
        self.proxy_partida = None
        self.jugador_cliente = None

        # Estado interno
        self._last_response = None
        self._state_lock = threading.Lock()

        # referencias al daemon local del cliente
        self._daemon = None
        self._daemon_thread = None
        self._nombre_logico_jugador = None

    def get_proxy_partida_singleton(self):
        if self.proxy_partida is None:
            try:
                self.proxy_partida = Pyro5.api.Proxy(f"PYRONAME:{self.nombre_logico_server}")
            except Pyro5.errors.NamingError:
                self.gui.show_error(f"Error: No se pudo encontrar el objeto '{self.nombre_logico_server}'.")
                self.gui.show_message("Asegúrese de que el Servidor de Nombres y el servidor.py estén en ejecución.")
                sys.exit(1)
        return self.proxy_partida

    def buscar_partida(self):
        try:
            ns = Pyro5.api.locate_ns()
            uri = ns.lookup(self.nombre_logico_server)
            self.gui.show_message(f"[Gestor] Partida encontrada (Deamon disponible) | URI: {uri}")
            return True
        except Pyro5.errors.NamingError:
            self.gui.show_error("[Gestor] No se encontró una Partida activa. Espere a que alguien cree una!")
            return False

    def ingresar_nickname_valido(self):
        nickname = self.gui.get_input("\nIngrese su NickName para la partida: ")
        formated_nickname = nickname.lower().replace(" ", "")

        respuesta = RespuestaRemotaJSON.deserializar(
            self.get_proxy_partida_singleton().CheckNickNameIsUnique(formated_nickname)
        )

        while not respuesta.exito:
            self.gui.show_error(f"{respuesta.mensaje}")
            nickname = self.gui.get_input("\nIngrese su NickName para la partida: ")
            formated_nickname = nickname.lower().replace(" ", "")
            respuesta = RespuestaRemotaJSON.deserializar(
                self.get_proxy_partida_singleton().CheckNickNameIsUnique(formated_nickname)
            )

        self.jugador_cliente = JugadorCliente(nickname)

        self.inicializar_Deamon_Cliente(
            self.jugador_cliente.get_nickname(),
            self.jugador_cliente.get_nombre_logico()
        )
        self.gui.show_message(f"NickName '{nickname}' confirmado!")

    def inicializar_Deamon_Cliente(self, nickname: str, nombre_logico_jugador: str):
        ip_cliente = ComunicationHelper.obtener_ip_local()
        # Crear el objeto remoto y pasar el gestor (self)
        objeto_cliente = ServicioCliente(self.gui, self)

        # nombre lógico con prefijo "jugador.<nickname>"
        self._nombre_logico_jugador = f"jugador.{nickname}"

        def daemon_loop():
            # Crear y guardar el daemon para poder apagarlo despues
            self._daemon = Pyro5.api.Daemon(host=ip_cliente)
            try:
                uri = ComunicationHelper.registrar_objeto_en_ns(objeto_cliente, self._nombre_logico_jugador, self._daemon)
                self.gui.show_message(f"[Registro] Objeto CLIENTE '{nickname}' disponible en URI: {uri}")
            except Exception as e:
                self.gui.show_error(f"No se pudo registrar el objeto en NS: {e}")
                # aun así arrancamos el requestLoop para aceptar conexiones directas si corresponde
            # loop de requests (bloqueante)
            self._daemon.requestLoop()

        # arrancar daemon en hilo de fondo
        self._daemon_thread = threading.Thread(target=daemon_loop, daemon=True)
        self._daemon_thread.start()

        # pequeña espera (mejor: sincronizar con evento; sleep está bien para prototipo)
        time.sleep(1)

    def stop_daemon_cliente(self):
        # apagar daemon y limpiar registro en NS
        if self._daemon:
            try:
                self._daemon.shutdown()
            except Exception:
                pass
        if self._daemon_thread:
            self._daemon_thread.join(timeout=2)

        # opcional: remover del nameserver
        try:
            ns = Pyro5.api.locate_ns()
            ns.remove(self._nombre_logico_jugador)
        except Exception:
            pass

    def unirse_a_sala(self):
        self.gui.show_message(f"Jugador '{self.jugador_cliente.get_nickname()}' uniendose a la sala...")
        json = self.get_proxy_partida_singleton().unirse_a_sala(
            self.jugador_cliente.get_nickname(),
            self.jugador_cliente.get_nombre_logico()
        )

        respuesta: RespuestaRemotaJSON = RespuestaRemotaJSON.deserializar(json)
        print("AAAAAAAAAAAAAAa")
        self.gui.show_message(respuesta.mensaje)
        if respuesta.exito:
            self.gui.show_message(f"Jugadores en la sala: {respuesta.datos}")
        #if not respuesta.exito:


        #self.gui.show_message(f"Jugador '{self.jugador_cliente.get_nickname()}' se ha unido a la sala!")

    def confirmar_jugador_partida(self):
        self.gui.show_message(f"Confirmando jugador: '{self.jugador_cliente.get_nickname()}'....")
        self.get_proxy_partida_singleton().confirmar_jugador(self.jugador_cliente.get_nickname())
        #self.gui.show_message(f"Jugador: '{self.jugador_cliente.get_nickname()}' Confirmado. Espere a que inicie la ronda.")

    # --- métodos que ServicioCliente llamará (callbacks locales) ---
    def on_info(self, tipo: str, info: str):
        # llamado por ServicioCliente cuando llega un evento
        # proteger estado con lock
        with self._state_lock:
            # podés guardar historial, mostrar en GUI, etc.
            self._last_response = f"{tipo}:{info}"
        # ejemplo: actualizar GUI (si la GUI necesita operar en hilo principal, coordiná eso)
        try:
            self.gui.show_message(f"[Gestor Cliente] ({tipo}) {info}")
        except Exception:
            pass

    def provide_response(self) -> str:
        with self._state_lock:
            return self._last_response or ""

    def jugar_nueva_ronda(self):
        # instanciar objeto de RondaCliente
        # al final obtener diccionario para mandar a servidor -> uso de RondaCliente.getRespuestasJugador
        pass