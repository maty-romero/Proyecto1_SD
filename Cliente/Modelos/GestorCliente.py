import socket
import sys
import threading
import time
import Pyro5

from Cliente.Modelos.JugadorCliente import JugadorCliente
from Cliente.Modelos.ServicioCliente import ServicioCliente
from Cliente.Modelos.SesionClienteSocket import SesionClienteSocket
from Cliente.Utils.ComunicationHelper import ComunicationHelper
from Cliente.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Utils.SerializeHelper import SerializeHelper


class GestorCliente:
    def __init__(self):
        self.logger = ConsoleLogger(name="GestorCliente", level="INFO")
        self.nombre_logico_server = "gestor.partida"
        self.proxy_partida = None
        self.Jugador_cliente = None

        # Estado interno (para ServicioCliente) - recepcion
        self._last_response = None
        self._state_lock = threading.Lock()

        # referencias al daemon local del cliente
        self._daemon = None
        self._daemon_thread = None

    def get_proxy_partida_singleton(self):
        if self.proxy_partida is None:
            try:
                self.proxy_partida = Pyro5.api.Proxy(f"PYRONAME:{self.nombre_logico_server}")
            except Pyro5.errors.NamingError:
                self.logger.error(f"Error: No se pudo encontrar el objeto '{self.nombre_logico_server}'.")
                self.logger.error("Asegúrese de que el Servidor de Nombres y el servidor.py estén en ejecución.")
                sys.exit(1)
        return self.proxy_partida

    def buscar_partida(self):
        try:
            ns = Pyro5.api.locate_ns()
            uri = ns.lookup(self.nombre_logico_server)
            self.logger.info(f"Partida encontrada (Deamon disponible) | URI: {uri}")
            return True
        except Pyro5.errors.NamingError:
            self.logger.error(f"No se encontró una Partida activa. Espere a que alguien cree una!")
            return False

    def solicitar_acceso_sala(self):
        self.logger.info("Solicitando acceso a servidor remoto")
        resultado_dict = self.get_proxy_partida_singleton().solicitar_acceso()
        self.logger.info(f"Solicitud acceso: {resultado_dict}")
        return resultado_dict

    def unirse_a_sala(self, formated_nickname):
        """
            solicitar_acceso -> verificar y mostrar en pantalla.
            ingresar nicknameValido
            inicializar deamon Cliente
            abrir Socket Cliente
            registrar_cliente(json_infoConexion y Cliente)
            respuesta Server a Cliente -  via Pyro (Mismo return de ServicioJuego)
            Mostrar info Sala
        """
        resu_dict = self.solicitar_acceso_sala()
        if not resu_dict['exito']:
            self.logger.info(resu_dict['msg'])
            sys.exit() # no puede jugar

        # ingreso nickname
        # breakpoint()
        nickname_valido = formated_nickname
        
        #nickname_valido = self.ingresar_nickname_valido(formated_nickname)

        self.logger.info(f"NickName '{nickname_valido}' disponible!")
        # inicializacion deamon Cliente y sesion de socket
        self.Jugador_cliente = JugadorCliente(nickname_valido)
        self.inicializar_Deamon_Cliente()

        """
        # ******** SIMULACION MULTIPLES CLIENTES EN UNA MAQUINA
        # Obtener puerto libre
        s_temp = socket.socket()
        s_temp.bind(('localhost', 0))
        puerto_libre = s_temp.getsockname()[1]
        s_temp.close()
        self.logger.info(f"|SIMULACION N CLIENTES| => Cliente '{nickname_valido}' escuchando en puerto {puerto_libre}")

        # Iniciar sesión socket en puerto dinámico
        self.iniciar_sesion_socket_en_hilo(puerto_libre)
        # ******** SIMULACION MULTIPLES CLIENTES EN UNA MAQUINA
        --> comentar: self.iniciar_sesion_socket_en_hilo(5555)  # puerto fijo para todos los clientes?
        """

        self.iniciar_sesion_socket_en_hilo(5555)  # puerto fijo para todos los clientes?
        # espera a que sesion socket este listo
        self.Jugador_cliente.sesion_socket.socket_listo_event.wait(timeout=5)
        self.logger.info("Sesion Socket iniciada, esperando que alguien se conecte...")

        self.logger.info(f"Jugador '{self.Jugador_cliente.get_nickname()}' uniendose a la sala...")

        # registro del cliente
        info_cliente = self.Jugador_cliente.to_dict()  # dict con info relevante
        resultado_dict = self.get_proxy_partida_singleton().unirse_a_sala(info_cliente)
        self.logger.info(f"Jugador '{self.Jugador_cliente.get_nickname()}' se ha unido a la sala!")
        self.logger.info(f"InfoSala: {resultado_dict}")
        

        # REFACTORIZAR POR ALGO MEJOR - Tal vez con eventos?
        # try:
        #     self.logger.error("**** Iniciando loop cliente ****")
        #     self.logger.error("\nPresione [CTRL + C] para terminar hilo principal Cliente")
        #     while True:
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     self.jugador_cliente.sesion_socket.cerrar()
        #     print("Sesión cerrada por interrupción.")


    
    #usamos en controladorSalaView
    def ingresar_nickname_valido(self,formated_nickname) -> str:
        # nickname = input("\nIngrese su NickName para la partida: ") #### ACÁ PIDE EL INPUT DEL CLIENTE
        # formated_nickname = nickname.lower().replace(" ", "")
        #Mandamos acá el nickname ya formateado desde el ControladorNickname
        resu_dict = self.get_proxy_partida_singleton().CheckNickNameIsUnique(formated_nickname)
        return resu_dict # Devuelve un diccionario con 'exito' y 'msg'
        # while not resu_dict['exito']:
        #     print(f"\n**{resu_dict['msg']}")
        #     #nickname = input("\nIngrese su NickName para la partida: ")
        #     formated_nickname = nickname.lower().replace(" ", "")
        #     resu_dict = self.get_proxy_partida_singleton().CheckNickNameIsUnique(formated_nickname)
            
        #     return {'exito': False, 'msg': resu_dict['msg']}  # Retorna el error para que lo maneje el controlador
        # return {'exito': True, 'msg': "Nickname disponible"}  
        #return formated_nickname

    # Sesiones o Servicios Cliente a Utilizar

    def iniciar_sesion_socket_en_hilo(self, puerto: int):
        try:
            self.Jugador_cliente.sesion_socket = SesionClienteSocket(
                puerto_fijo=puerto,
                callback_mensaje=self._procesar_mensaje_socket,
                nickname_log=self.Jugador_cliente.get_nickname()
            )

            hilo_socket = threading.Thread(
                target=self.Jugador_cliente.sesion_socket.iniciar,
                daemon=True
            )
            hilo_socket.start()

        except Exception as e:
            self.logger.error(f"[iniciar_sesion_socket_en_hilo] Ex: {e}")

        #self.jugador_cliente.sesion_socket.iniciar()

    # Funcion CallBack para Socket
    def _procesar_mensaje_socket(self, mensaje):
        try:
            exito, msg, datos = SerializeHelper.deserializar(mensaje)
            """
            if not exito:
                self.logger.warning(f"[Socket] Error recibido: {msg}")
                return
            """
            self.logger.info(f"[Socket] Mensaje recibido: {msg}")

            # Procesar según tipo de mensaje
            if msg == "nueva_ronda":
                #self._actualizar_estado_ronda(datos)
                self.logger.info(f"MENSAJE RECIBIDO POR SOCKET: exito:{exito}, msg:'{msg}', datos:{datos}")
            elif msg == "fin_partida":
                #self._cerrar_partida(datos)
                pass
            else:
                self.logger.warning(f"[Socket] Otro Mensaje: {msg}")

        except Exception as e:
            self.logger.error(f"[Socket] Error al procesar mensaje: {e}")

    def inicializar_Deamon_Cliente(self):
        ip_cliente = ComunicationHelper.obtener_ip_local()
        objeto_cliente = ServicioCliente(self)  # Se crea objeto remoto y se pasa el gestor (self)

        # nom_logico ya definido con prefijo "jugador.<nickname>"
        nombre_logico: str= self.Jugador_cliente.get_nombre_logico()

        def daemon_loop():
            # Crear y guardar el daemon para poder apagarlo despues
            self._daemon = Pyro5.api.Daemon(host=ip_cliente)
            try:
                uri = ComunicationHelper.registrar_objeto_en_ns(objeto_cliente, nombre_logico, self._daemon)
                self.logger.info(f"[Deamon] Objeto CLIENTE '{self.Jugador_cliente.get_nickname()}' disponible en URI: {uri}")
            except Exception as e:
                self.logger.error(f"No se pudo registrar el objeto cliente en NS: {e}")
                # aun así arrancamos el requestLoop para aceptar conexiones directas si corresponde

            self._daemon.requestLoop() # loop de requests (bloqueante)

        # arrancar daemon en hilo de fondo
        self._daemon_thread = threading.Thread(target=daemon_loop, daemon=True)
        self._daemon_thread.start()

        # pequeña espera (mejor: sincronizar con evento; sleep está bien para prototipo)
        time.sleep(2)

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
            ns.remove(self.Jugador_cliente.get_nombre_logico())
        except Exception:
            pass

    def confirmar_jugador_partida(self):
        self.gui.show_message(f"Confirmando jugador: '{self.Jugador_cliente.get_nickname()}'....")
        msg = self.get_proxy_partida_singleton().confirmar_jugador(self.Jugador_cliente.get_nickname())
        self.gui.show_message(msg['msg'])

    def get_info_sala(self):
        return self.get_proxy_partida_singleton().get_sala()

"""
    # --- métodos que ServicioCliente llamará (callbacks locales) ---
    def on_info(self, tipo: str, info: str):
        # llamado por ServicioCliente cuando llega un evento
        # proteger estado con lock
        with self._state_lock:
            # podés guardar historial, mostrar en GUI, etc.
            self._last_response = info
            #self._last_response = f"{tipo}:{info}"
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

"""