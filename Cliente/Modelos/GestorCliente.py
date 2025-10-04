import queue
import socket
import sys
import threading
import time
import Pyro5

from Cliente.Controladores.ControladorNavegacion import ControladorNavegacion
from Cliente.Modelos.JugadorCliente import JugadorCliente
from Cliente.Modelos.ServicioCliente import ServicioCliente
from Utils.ManejadorSocket import ManejadorSocket
from Utils.ComunicationHelper import ComunicationHelper
from Utils.ConsoleLogger import ConsoleLogger
from Utils.SerializeHelper import SerializeHelper

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

#COLOCAR LA IP DEL NS
IP_NS = ComunicationHelper.obtener_ip_local()

#ip_local = socket.gethostbyname(socket.gethostname())
#IP_NS = socket.gethostbyname(socket.gethostname())
   # DESKTOP-HUREDOL
PUERTO_NS = 9090


class GestorCliente:
    def __init__(self):
        self.logger = ConsoleLogger(name="GestorCliente", level="INFO")
        self.nombre_logico_server = "gestor.partida"
        self.proxy_partida = None
        self.Jugador_cliente: JugadorCliente = None
        self.controlador_navegacion = None
        
        self.hostNS = IP_NS
        self.puertoNS = PUERTO_NS
        
        print(f"NameServer name : {self.hostNS}")
        
        # Estado interno (para ServicioCliente) - recepcion
        self._last_response = None
        self._state_lock = threading.Lock()

        # referencias al daemon local del cliente
        self._daemon = None
        self._daemon_thread = None

        # referencias a controladores
        self.controlador_navegacion = None
        self.ya_se_unio = False

    def registrar_controlador_navegador(self, controlador: ControladorNavegacion):
        self.controlador_navegacion = controlador

    def get_proxy_partida_singleton(self):
        if self.proxy_partida is None:
            try:

                ns = Pyro5.api.locate_ns(host=self.hostNS, port=self.puertoNS)
                uri = ns.lookup(self.nombre_logico_server)
                self.proxy_partida = Pyro5.api.Proxy(uri)
                self.logger.info(f"PYRONAME:{self.nombre_logico_server}")
                self.logger.info(uri)
            except Pyro5.errors.NamingError:
                self.logger.error(f"Error: No se pudo encontrar el objeto '{self.nombre_logico_server}'.")
                self.logger.error("Asegúrese de que el Servidor de Nombres y el servidor.py estén en ejecución.")
                sys.exit(1)

        # Reclamar propiedad del proxy en el hilo actual
        self.proxy_partida._pyroClaimOwnership()
        return self.proxy_partida

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
        if self.ya_se_unio:
            self.logger.warning("Ya se ejecutó unirse_a_sala. Ignorando segundo intento.")
            return
        self.ya_se_unio = True
        resu_dict = self.solicitar_acceso_sala()
        if not resu_dict['exito']:
            self.logger.info(resu_dict['msg'])
            sys.exit() # no puede jugar

        # ingreso nickname
        nickname_valido = formated_nickname
        
        self.logger.info(f"NickName '{nickname_valido}' disponible!")
        # inicializacion deamon Cliente y sesion de socket
        if self.Jugador_cliente is None:
            self.Jugador_cliente = JugadorCliente(nickname_valido)
        else:
            self.logger.warning("Jugador ya inicializado. Ignorando duplicado.")

        uri = self.inicializar_Daemon_Cliente()


        # ******** SIMULACION MULTIPLES CLIENTES EN UNA MAQUINA
        # Obtener puerto libre
        s_temp = socket.socket()
        s_temp.bind(('localhost', 0))
        puerto_libre = s_temp.getsockname()[1]
        s_temp.close()
        self.logger.warning(f"|SIMULACION N CLIENTES| => Cliente '{nickname_valido}' escuchando en puerto {puerto_libre}")

        # Iniciar sesión socket en puerto dinámico
        if hasattr(self.Jugador_cliente, "sesion_socket") and self.Jugador_cliente.sesion_socket is not None:
            self.logger.warning("Sesión de socket ya iniciada. Ignorando segundo intento.")
            return
        else:
            self.logger.warning("se inicia sesion de socket en hilo")
            self.iniciar_sesion_socket_en_hilo(puerto_libre)
            self.logger.warning("se termino de iniciar sesion de socket en hilo")

        self.Jugador_cliente.sesion_socket.socket_listo_event.wait(timeout=5)
        self.logger.info("Sesion Socket iniciada, esperando que alguien se conecte...")
        self.logger.info(f"Jugador '{self.Jugador_cliente.get_nickname()}' uniendose a la sala...")
        # registro del cliente
        info_cliente = self.Jugador_cliente.to_dict()  # dict con info relevante
        info_cliente['uri'] = uri

        resultado_dict = self.get_proxy_partida_singleton().unirse_a_sala(info_cliente)
        self.logger.warning(f"Jugador '{self.Jugador_cliente.get_nickname()}' se ha unido a la sala!")
        self.logger.warning(f"InfoSala: {resultado_dict}")
   
    #usamos en controladorSalaView
    def ingresar_nickname_valido(self,formated_nickname) -> str:
        resu_dict = self.get_proxy_partida_singleton().CheckNickNameIsUnique(formated_nickname)
        return resu_dict # Devuelve un diccionario con 'exito' y 'msg'

    # Sesiones o Servicios Cliente a Utilizar

    def iniciar_sesion_socket_en_hilo(self, puerto: int):
        try:

            self.Jugador_cliente.sesion_socket = ManejadorSocket(
                host=ComunicationHelper.obtener_ip_local(),
                puerto=puerto,
                callback_mensaje=self._procesar_mensaje_socket,
                nombre_logico=self.Jugador_cliente.get_nickname(),
                es_servidor=False,
                tipo_Nodo="SesionCliente"
            )

            hilo_socket = threading.Thread(
                target=self.Jugador_cliente.sesion_socket.iniciar_manejador,
                daemon=True
            )
            hilo_socket.start()

        except Exception as e:
            self.logger.error(f"[iniciar_sesion_socket_en_hilo] Ex: {e}")


    # Funcion CallBack para Socket
    def _procesar_mensaje_socket(self, mensaje):
        try:
            # Manejar HEARTBEAT que no es JSON
            if mensaje == "HEARTBEAT":
                return  # Los heartbeats se procesan automáticamente en ManejadorSocket
            
            exito, msg, datos = SerializeHelper.deserializar(mensaje)
            """
            if not exito:
                self.logger.warning(f"[Socket] Error recibido: {msg}")
                return
            """
            self.logger.info(f"[Socket] Mensaje recibido: {msg}")
            # Procesar según tipo de mensaje
            if msg == "nuevo_jugador_sala":
                self.logger.warning("Recepcion mje Socket: nuevo_jugador_sala")
                nickname = datos.get("nickname", "¿?")
                mensaje_estado = f"Se ha unido '{nickname}' a la sala"
                self.controlador_navegacion.controlador_sala.cambiar_estado_sala(mensaje_estado)
            elif msg == "en_sala":
                self.controlador_navegacion.mostrar('sala')
            elif msg == "info_sala":
                self.logger.info("Recibido estado de sala - navegando y rehabilitando botón")
                self.controlador_navegacion.mostrar('sala')
            elif msg == "nueva_ronda":
                self.logger.info(f"MENSAJE RECIBIDO POR SOCKET: exito:{exito}, msg:'{msg}', datos:{datos}")
                self.controlador_navegacion.controlador_ronda.habilitar_btn_stop()
                self.controlador_navegacion.mostrar('ronda')
            elif msg == "fin_ronda":
                self.logger.info(f"FIN RONDA: exito:{exito}, msg:'{msg}', datos:{datos}")
                self.controlador_navegacion.controlador_ronda.marcar_fin_ronda()
                self.controlador_navegacion.mostrar('votaciones')
            elif msg == "inicio_votacion":
                self.logger.warning(f"inicio_votacion => datos: {datos}")
            elif msg == "estado_votaciones":
                self.logger.info("Restaurando estado de votaciones tras reconexión")
                self.controlador_navegacion.controlador_votaciones.mostrar_info_votaciones(datos)
            elif msg == "aviso_tiempo_votacion":
                self.logger.info(f"Recibido del server {datos}")
                self.controlador_navegacion.controlador_votaciones.actualizar_mensaje_timer(datos)
            elif msg == "tiempo_votacion_agotado":
                mensaje = datos.get('mensaje', 'Tiempo agotado') if isinstance(datos, dict) else datos
                self.logger.info(f"Tiempo de votación agotado: {mensaje}")
                self.controlador_navegacion.controlador_votaciones.mostrar_tiempo_agotado(datos)
            elif msg == "fin_partida":
                self.logger.info("La partida ha finalizado.")
                self.controlador_navegacion.controlador_resultados.mostrar_resultados(datos)
                self.controlador_navegacion.mostrar('resultados')
            elif msg == "cerrar_sala":
                self.controlador_navegacion.mostrar('cerrar_sala')
            elif msg == "SERVIDOR_DESCONECTADO":
                motivo = datos.get("motivo", "Motivo desconocido")
                self.logger.warning(f" SERVIDOR DESCONECTADO ({motivo}) - Mostrando vista de reconexión")
                self._manejar_desconexion_servidor()
            elif msg == "servidor_recuperado":
                self.logger.info(" SERVIDOR RECUPERADO - Ocultando vista de reconexión")
                self._manejar_servidor_recuperado(datos if 'datos' in locals() else None)
            elif msg == "CONEXION_RESTAURADA":
                self.logger.info(" CONEXIÓN RESTAURADA - Cliente detectó reconexión")
                # Nota: La notificación oficial vendrá del servidor
            else:
                self.logger.warning(f"[Socket] Otro Mensaje: {msg}")

        except Exception as e:
            self.logger.error(f"[Socket] Error al procesar mensaje: {e}")

    
    def inicializar_Daemon_Cliente(self):
        if self._daemon is not None:
            self.logger.warning("Daemon ya inicializado. Ignorando segundo intento.")
            return None
        ip_cliente = ComunicationHelper.obtener_ip_local()
        objeto_cliente = ServicioCliente(self)
        nombre_logico: str = self.Jugador_cliente.get_nombre_logico()

        # Cola para pasar la URI desde el hilo
        uri_queue = queue.Queue()

        def daemon_loop():
            self._daemon = Pyro5.api.Daemon(host=ip_cliente)
            try:
                ns = Pyro5.api.locate_ns(self.hostNS, self.puertoNS)
                #ns = Pyro5.api.locate_ns()
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
    
    def enviar_cerrar_sala(self):
        try:
            with Pyro5.api.locate_ns(host=self.hostNS, port=self.puertoNS) as ns:
                uri = ns.lookup(self.nombre_logico_server)
                proxy = Pyro5.api.Proxy(uri)
                proxy.recibir_cerrar_sala()
        except Exception as e:
            self.logger.error(f"Error enviando señal de cierre: {e}")
    
    """Modificar para que busque a remoto con ip y port"""
    def enviar_stop(self):

        try:
            #with Pyro5.api.locate_ns() as ns:
            with Pyro5.api.locate_ns(host=self.hostNS, port=self.puertoNS) as ns:
                uri = ns.lookup(self.nombre_logico_server)
                proxy = Pyro5.api.Proxy(uri)
                proxy.recibir_stop()
        except Exception as e:
            self.logger.error(f"Error enviando stop: {e}")

    def provide_response(self):
        #se obtienenen las respuestas de RondaCliente
        return self.controlador_navegacion.obtener_respuestas_ronda()

    def cargar_datos_vista_votacion(self,respuestas_clientes):
        self.controlador_navegacion.controlador_votaciones.mostrar_info_votaciones(respuestas_clientes)

    def enviar_votos_jugador(self):
        return self.controlador_navegacion.controlador_votaciones.enviar_votos()

    def _manejar_desconexion_servidor(self):
        """Maneja la desconexión del servidor mostrando vista de reconexión"""
        try:
            # Mostrar vista de mensaje transitorio con información de reconexión
            if hasattr(self.controlador_navegacion, 'controlador_mensaje'):
                self.controlador_navegacion.controlador_mensaje.mostrar_mensaje_reconexion(
                    "Conexión perdida con el servidor",
                    "Esperando reconexión automática...",
                    mostrar_botones=False
                )
            
            self.controlador_navegacion.mostrar("mensaje")
            self.logger.info("Vista de reconexión mostrada al usuario")
            
        except Exception as e:
            self.logger.error(f"Error mostrando vista de reconexión: {e}")

    def _manejar_servidor_recuperado(self, datos=None):
        """Maneja la recuperación del servidor ocultando vista de reconexión"""
        try:
            # Ocultar vista de reconexión y volver a la vista anterior
            mensaje_recuperacion = "Conexión restablecida"
            if datos and isinstance(datos, dict):
                mensaje_recuperacion = datos.get("mensaje", mensaje_recuperacion)
            
            self.logger.info(f"Servidor recuperado: {mensaje_recuperacion}")
            
            # CRÍTICO: Reconectar proxy Pyro5
            self.logger.info("Reconectando proxy Pyro5...")
            self._reconectar_proxy_pyro5()
            
            # Mostrar brevemente mensaje de éxito
            if hasattr(self.controlador_navegacion, 'controlador_mensaje'):
                self.controlador_navegacion.controlador_mensaje.mostrar_mensaje_reconexion(
                    "¡Conexión restablecida!",
                    f"{mensaje_recuperacion}\nEsperando sincronización...",
                    mostrar_botones=False,
                )
            # No forzar navegación - el servidor enviará el estado correcto automáticamente
            self.logger.info("Esperando que el servidor envíe el estado actual de la partida...")
            
        except Exception as e:
            self.logger.error(f"Error manejando recuperación de servidor: {e}")
            # En caso de error, mostrar mensaje y esperar estado del servidor
            if hasattr(self.controlador_navegacion, 'controlador_mensaje'):
                self.controlador_navegacion.controlador_mensaje.mostrar_mensaje_reconexion(
                    "Error en reconexión",
                    "Reintentando sincronización...",
                    mostrar_botones=False,
                )

    def _reconectar_proxy_pyro5(self):
        """Reconecta el proxy Pyro5 después de la recuperación del servidor"""
        try:
            # Limpiar proxy existente
            self.proxy_partida = None
            
            # Esperar un momento para que el servidor esté completamente listo
            import time
            time.sleep(1)
            # Reconectar usando el método existente
            self.get_proxy_partida_singleton()
            if self.proxy_partida:
                self.logger.info("✅ Proxy Pyro5 reconectado exitosamente")
            else:
                self.logger.warning("❌ No se pudo reconectar proxy Pyro5")
        except Exception as e:
            self.logger.error(f"Error reconectando proxy Pyro5: {e}")
            # Intentar una segunda vez
            try:
                time.sleep(2)
                self.get_proxy_partida_singleton()
                self.logger.info("✅ Proxy Pyro5 reconectado en segundo intento")
            except Exception as e2:
                self.logger.error(f"Fallo definitivo reconectando proxy Pyro5: {e2}")

