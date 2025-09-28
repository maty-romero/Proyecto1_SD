import queue
import socket
import sys
import threading
import time
import Pyro5

from Cliente.Controladores.ControladorNavegacion import ControladorNavegacion
from Cliente.Modelos.JugadorCliente import JugadorCliente
from Cliente.Modelos.ServicioCliente import ServicioCliente
from Cliente.Modelos.SesionClienteSocket import SesionClienteSocket
from Cliente.Utils.ComunicationHelper import ComunicationHelper
from Cliente.Utils.ConsoleLogger import ConsoleLogger
from Cliente.Utils.SerializeHelper import SerializeHelper

"""Para el uso en docker, un compose de la siguiente forma:

    services:
  nameserver:
    image: python:3.12
    container_name: pyro_ns
    networks:
      - pyro_net

  servidor:
    build: ./servidor
    depends_on:
      - nameserver
    networks:
      - pyro_net

  cliente:
    build: ./cliente
    depends_on:
      - servidor
    networks:
      - pyro_net

networks:
  pyro_net:
    driver: bridge

    
    Permite lo siguiente

    ns = Pyro5.api.locate_ns(host="nameserver", port=9090)

"""
NOMBRE_PC_NS = "192.168.151.176"   # DESKTOP-HUREDOL
PUERTO_NS = 9090


class GestorCliente:
    def __init__(self):
        self.logger = ConsoleLogger(name="GestorCliente", level="INFO")
        self.nombre_logico_server = "gestor.partida"
        self.proxy_partida = None
        self.Jugador_cliente: JugadorCliente = None
        self.controlador_navegacion = None
        
        self.puertoNS = PUERTO_NS
        self.hostNS = NOMBRE_PC_NS
        #self.hostNS = str(ComunicationHelper.obtener_ip_local())
        print(f"NameServer name : {self.hostNS}")
        
        # Estado interno (para ServicioCliente) - recepcion
        self._last_response = None
        self._state_lock = threading.Lock()

        # referencias al daemon local del cliente
        self._daemon = None
        self._daemon_thread = None

        # referencias a controladores
        self.controlador_navegacion = None

    def registrar_controlador_navegador(self, controlador: ControladorNavegacion):
        self.controlador_navegacion = controlador

    def get_proxy_partida_singleton(self):
        if self.proxy_partida is None:
            try:
                with Pyro5.api.locate_ns(host=self.hostNS, port=self.puertoNS) as ns:
                    uri = ns.lookup(self.nombre_logico_server)
                    self.proxy_partida = Pyro5.api.Proxy(uri)
                    #self.proxy_partida = Pyro5.api.Proxy(f"PYRONAME:{self.nombre_logico_server}")
                    print(f"PYRONAME:{self.nombre_logico_server}")
                    print(uri)
            except Pyro5.errors.NamingError:
                self.logger.error(f"Error: No se pudo encontrar el objeto '{self.nombre_logico_server}'.")
                self.logger.error("Asegúrese de que el Servidor de Nombres y el servidor.py estén en ejecución.")
                sys.exit(1)

        # Reclamar propiedad del proxy en el hilo actual
        self.proxy_partida._pyroClaimOwnership()
        return self.proxy_partida

    """NUEVO METODO PARA CONEXION A REMOTO EN MISMA RED LOCAL - Puede cambiarse para usar los valores globales"""
    # def get_proxy_partida_singleton(self):
    #     if self.proxy_partida is None:
    #         try:
    #             # Conexión al NameServer remoto usando IP y puerto
    #             with Pyro5.api.locate_ns(host=self.hostNS, port=self.puertoNS) as ns:
    #                 uri = ns.lookup(self.nombre_logico_server)
    #                 self.proxy_partida = Pyro5.api.Proxy(uri)
    #         except Pyro5.errors.NamingError:
    #             print(f"Error: No se pudo encontrar el objeto '{self.nombre_logico_server}' en {self.hostNS}:{self.puertoNS}")
    #             raise
    #     # Reclamar propiedad del proxy en el hilo actual si es necesario
    #     self.proxy_partida._pyroClaimOwnership()
    #     return self.proxy_partida

    def buscar_partida(self):
        try:
            #ns = Pyro5.api.locate_ns()
            ns = Pyro5.api.locate_ns(self.hostNS,self.puertoNS)
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
        uri = self.inicializar_Deamon_Cliente()


        # ******** SIMULACION MULTIPLES CLIENTES EN UNA MAQUINA
        # Obtener puerto libre
        s_temp = socket.socket()
        s_temp.bind(('localhost', 0))
        puerto_libre = s_temp.getsockname()[1]
        s_temp.close()
        self.logger.warning(f"|SIMULACION N CLIENTES| => Cliente '{nickname_valido}' escuchando en puerto {puerto_libre}")

        # Iniciar sesión socket en puerto dinámico
        self.iniciar_sesion_socket_en_hilo(puerto_libre)
        # ******** SIMULACION MULTIPLES CLIENTES EN UNA MAQUINA
        """
        --> comentar: self.iniciar_sesion_socket_en_hilo(5555)  # puerto fijo para todos los clientes?
        """

        #self.iniciar_sesion_socket_en_hilo(5555)  # puerto fijo para todos los clientes?
        # espera a que sesion socket este listo
        self.Jugador_cliente.sesion_socket.socket_listo_event.wait(timeout=5)
        self.logger.info("Sesion Socket iniciada, esperando que alguien se conecte...")
        self.logger.info(f"Jugador '{self.Jugador_cliente.get_nickname()}' uniendose a la sala...")
        # registro del cliente
        info_cliente = self.Jugador_cliente.to_dict()  # dict con info relevante
        info_cliente['uri'] = uri
        resultado_dict = self.get_proxy_partida_singleton().unirse_a_sala(info_cliente)
        self.logger.warning(f"Jugador '{self.Jugador_cliente.get_nickname()}' se ha unido a la sala!")
        self.logger.warning(f"InfoSala: {resultado_dict}")
        

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
        resu_dict = self.get_proxy_partida_singleton().CheckNickNameIsUnique(formated_nickname)
        return resu_dict # Devuelve un diccionario con 'exito' y 'msg'

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
            if msg == "nuevo_jugador_sala":
                self.logger.warning("Recepcion mje Socket: nuevo_jugador_sala")
                nickname = datos.get("nickname", "¿?")
                mensaje_estado = f"Se ha unido '{nickname}' a la sala"
                self.controlador_navegacion.controlador_sala.cambiar_estado_sala(mensaje_estado)
            # Procesar según tipo de mensaje
            elif msg == "en_sala":
                self.controlador_navegacion.mostrar('sala')
            elif msg == "nueva_ronda":
                #self._actualizar_estado_ronda(datos)
                self.logger.info(f"MENSAJE RECIBIDO POR SOCKET: exito:{exito}, msg:'{msg}', datos:{datos}")
                self.controlador_navegacion.controlador_ronda.habilitar_btn_stop()
                self.controlador_navegacion.mostrar('ronda')
            elif msg == "fin_ronda":
                self.logger.info(f"FIN RONDA: exito:{exito}, msg:'{msg}', datos:{datos}")
                self.controlador_navegacion.controlador_ronda.marcar_fin_ronda()
                self.controlador_navegacion.mostrar('votaciones')
            elif msg == "inicio_votacion":
                self.logger.warning(f"inicio_votacion => datos: {datos}")
            elif msg == "aviso_tiempo_votacion":
                self.logger.info(f"Recibido del server {datos}")
                self.controlador_navegacion.controlador_votaciones.actualizar_mensaje_timer(datos)
            elif msg == "fin_partida":
                self.logger.info("La partida ha finalizado.")
                self.controlador_navegacion.controlador_resultados.mostrar_resultados(datos)
                self.controlador_navegacion.mostrar('resultados')
                #self.stop_daemon_cliente()
            else:
                self.logger.warning(f"[Socket] Otro Mensaje: {msg}")

        except Exception as e:
            self.logger.error(f"[Socket] Error al procesar mensaje: {e}")
            
    
    def cerrar_app(self):
        import sys
        self.logger.info("Cerrando aplicación por decisión del usuario o timeout de reconexión.")
        sys.exit(0)
        
        
    def intentar_reconexion(self):
        # Arma el diccionario info_cliente igual que al inicio
        info_cliente = self.Jugador_cliente.to_dict()
        info_cliente['uri'] = self.inicializar_Deamon_Cliente()  # o el uri actual si ya está
        resultado = self.get_proxy_partida_singleton().unirse_a_sala(info_cliente)
        if resultado and resultado.get('exito'):
            # Pide al servidor que le mande la vista correcta
            self.get_proxy_partida_singleton().restaurar_vista_general(self.Jugador_cliente.get_nickname())
        else:
            self.cerrar_app()

    
    def inicializar_Deamon_Cliente(self):
        ip_cliente = ComunicationHelper.obtener_ip_local()
        objeto_cliente = ServicioCliente(self)
        nombre_logico: str = self.Jugador_cliente.get_nombre_logico()

        # Cola para pasar la URI desde el hilo
        uri_queue = queue.Queue()

        def daemon_loop():
            self._daemon = Pyro5.api.Daemon(host=ip_cliente)
            try:
                ns = Pyro5.api.locate_ns(self.hostNS, self.puertoNS)
                uri = ComunicationHelper.registrar_objeto_en_ns(objeto_cliente, nombre_logico, self._daemon, ns)
                self.logger.info(f"[Daemon] Objeto CLIENTE '{self.Jugador_cliente.get_nickname()}' disponible en URI: {uri}")
                uri_queue.put(uri)  # Enviar la URI al hilo principal
            except Exception as e:
                self.logger.error(f"No se pudo registrar el objeto cliente en NS: {e}")
                uri_queue.put(None)  # Enviar None si hubo error

            self._daemon.requestLoop()

        # Arrancar daemon en hilo de fondo
        self._daemon_thread = threading.Thread(target=daemon_loop, daemon=True)
        self._daemon_thread.start()

        # Esperar a que el hilo coloque la URI en la cola
        try:
            uri = uri_queue.get(timeout=5)  # Espera hasta 5 segundos
        except queue.Empty:
            uri = None
            self.logger.error("Timeout esperando la URI del objeto cliente")

        return uri


    """
    def inicializar_Deamon_Cliente(self):
        ip_cliente = ComunicationHelper.obtener_ip_local()
        objeto_cliente = ServicioCliente(self)  # Se crea objeto remoto y se pasa el gestor (self)

        # nom_logico ya definido con prefijo "jugador.<nickname>"
        nombre_logico: str= self.Jugador_cliente.get_nombre_logico()

        def daemon_loop():
            # Crear y guardar el daemon para poder apagarlo despues
            self._daemon = Pyro5.api.Daemon(host=ip_cliente)
            try:
                #ns = Pyro5.api.locate_ns()
                ns = Pyro5.api.locate_ns(self.hostNS, self.puertoNS)
                uri = ComunicationHelper.registrar_objeto_en_ns(objeto_cliente, nombre_logico, self._daemon, ns)
                self.logger.info(f"[Deamon] Objeto CLIENTE '{self.Jugador_cliente.get_nickname()}' disponible en URI: {uri}")
            except Exception as e:
                self.logger.error(f"No se pudo registrar el objeto cliente en NS: {e}")
                # aun así arrancamos el requestLoop para aceptar conexiones directas si corresponde

            self._daemon.requestLoop() # loop de requests (bloqueante)

        # arrancar daemon en hilo de fondo
        self._daemon_thread = threading.Thread(target=daemon_loop, daemon=True)
        self._daemon_thread.start()

        
        # pequeña espera (mejor: sincronizar con evento; sleep está bien para prototipo)
        #time.sleep(2)
    """

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
            ns = Pyro5.api.locate_ns(self.hostNS, self.puertoNS)
            ns.remove(self.Jugador_cliente.get_nombre_logico())
        except Exception:
            pass

    def confirmar_jugador_partida(self):
        self.logger.info(f"Confirmando jugador: '{self.Jugador_cliente.get_nickname()}'....")
        msg = self.get_proxy_partida_singleton().confirmar_jugador(self.Jugador_cliente.get_nickname())

    def set_controlador_navegacion(self, controlador):
        self.controlador_navegacion = controlador

    def get_info_sala(self):
        return self.get_proxy_partida_singleton().get_sala()
    
    def get_jugadores_min(self):
        return self.get_proxy_partida_singleton().get_jugadores_minimos()
    
    def get_jugadores_en_sala(self):
        return self.get_proxy_partida_singleton().ver_jugadores_partida()

    def get_info_ronda_act(self):
        return self.get_proxy_partida_singleton().get_info_ronda_actual()
    
    def get_proxy_partida(self):
        return self.get_proxy_partida_singleton()
    


    
    """Modificar para que busque a remoto con ip y port"""
    def enviar_stop(self):
        #proxy = Pyro5.api.Proxy(f"PYRONAME:{self.nombre_logico_server}")
        #proxy.recibir_stop()
        try:
            with Pyro5.api.locate_ns(host=self.hostNS, port=self.puertoNS) as ns:
                uri = ns.lookup(self.nombre_logico_server)
                proxy = Pyro5.api.Proxy(uri)
                proxy.recibir_stop()
        except Exception as e:
            self.logger.error(f"Error enviando stop: {e}")
    #------>
    # def enviar_stop(self):
    #     proxy = self.get_proxy_partida_singleton
    #     proxy.recibir_stop()

    def provide_response(self):
        #se obtienenen las respuestas de RondaCliente
        return self.controlador_navegacion.obtener_respuestas_ronda()

    def cargar_datos_vista_votacion(self,respuestas_clientes):
        self.controlador_navegacion.controlador_votaciones.mostrar_info_votaciones(respuestas_clientes)

    def enviar_votos_jugador(self):
        return self.controlador_navegacion.controlador_votaciones.enviar_votos()
    
    
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