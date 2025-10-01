import socket
import threading
import time
import traceback
from datetime import UTC, datetime, timedelta
from Utils.ConsoleLogger import ConsoleLogger
from Utils.SerializeHelper import SerializeHelper

class ManejadorSocket:
    def __init__(self, host: str, puerto: int, nombre_logico: str, callback_mensaje = None, es_servidor=False,tipo_Nodo:str=None):
        self.host = host
        self.puerto = puerto
        self.callback_mensaje = callback_mensaje
        self.es_servidor = es_servidor

        #Variable para determinar si se utiliza el hilo de heartbeat
        self.tipo_nodo = tipo_Nodo

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #es el socket de escucha
        self.conexiones = []  # lista de sockets conectados (para broadcast)

        #------------------metodos de logica de estado interno de escucha----------------------------------------------------------#
        self._escuchando = False    #se dejan ambos para evitar modificaciones a ultimo momento
        self.socket_listo_event = threading.Event()  # para saber cuándo el socket está listo
        #----------------------------------------------------------------------------#
        self.logger = ConsoleLogger(name=f"Socket[{nombre_logico}]", level="INFO")
        self.hilo_heartbeat = None

        # Estado para algoritmo Bully
        self.coordinador = None
        self.timestamp = None
        self.conectado = False

    def set_callback(self, callback):
        self.callback_mensaje = callback

    # ---------------------------
    # Inicializar como servidor
    # ---------------------------
    def iniciar_manejador(self):
        if self._escuchando:
            self.logger.warning("El manejador ya está activo.")
            return

        # Recrear el socket si fue cerrado
        if self.socket is None or self.socket.fileno() == -1:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.puerto))
            self.socket.listen()
            self._escuchando = True
            self.socket_listo_event.set()
            self.logger.info(f"Servidor escuchando en {self.host}:{self.puerto}")
            threading.Thread(target=self._aceptar_conexiones, daemon=True).start()

            self.logger.info(f"[DEBUG] Verificando si iniciar heartbeat: tipo_nodo='{self.tipo_nodo}', es_servidor={self.es_servidor}")
            if self.tipo_nodo=="SesionCliente" or self.es_servidor == False:
                self.logger.info(f"[DEBUG] Iniciando hilo heartbeat para tipo_nodo='{self.tipo_nodo}'")
                self.hilo_heartbeat = threading.Thread(target=self._enviar_heartbeat, daemon=True)
                self.hilo_heartbeat.start()
            else:
                self.logger.info(f"[DEBUG] NO se inicia heartbeat - condición no cumplida")

        except Exception as e:
            self.logger.error(f"Error al iniciar el manejador de socket: {e}")
            self._escuchando = False
            if self.socket:
                self.socket.close()
                self.socket = None
            
            traceback.print_exc()
    # ---------------------------
    # Conectar como cliente a otro nodo
    # ---------------------------
    def conectar_a_nodo(self, ip_destino, puerto_destino):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((ip_destino, puerto_destino))
            self.logger.info(f"Conectado a nodo en {ip_destino}:{puerto_destino}")
            if conn.fileno() != -1:
                self.conexiones.append(conn)
            self.logger.info(f"Registro de conexiones pos conexion:{self.conexiones}")
            # Asegurar que el estado permita escuchar
            if not self._escuchando:
                self._escuchando = True
                self.logger.info(f"[DEBUG] Activando _escuchando para conexión cliente")
            threading.Thread(target=self._escuchar, args=(conn,), daemon=True).start()
        except Exception as e:
            self.logger.error(f"Error al conectar con nodo: {e}")

    # ---------------------------
    # Aceptar nuevas conexiones (modo servidor)
    # ---------------------------
    def _aceptar_conexiones(self):
        while self._escuchando:
            try:
                conn, addr = self.socket.accept()
                self.conexiones.append(conn)
                self.logger.info(f"Nodo conectado desde {addr}")
                self.logger.info(f"Registro de conexiones pos aceptar conexion:{self.conexiones}")
                threading.Thread(target=self._escuchar, args=(conn,), daemon=True).start()
            except OSError as e:
                self.logger.warning(f"Error al aceptar conexión: {e}")
                break

    # ---------------------------
    # Escucha de mensajes para el cliente y para el servidor
    # ---------------------------
    def _escuchar(self, conn):
        # Para conexiones individuales, siempre escuchar mientras la conexión esté activa
        escuchando_activo = True
        self.logger.info(f"[DEBUG] Iniciando escucha en conexión. _escuchando global: {self._escuchando}")
        
        while escuchando_activo and (self._escuchando or conn in self.conexiones):
            try:
                data = conn.recv(1024)
                if not data:
                    self.logger.warning(f"Conexión cerrada por el otro extremo")
                    # Notificar desconexión del servidor al callback
                    if self.callback_mensaje and self.tipo_nodo == "SesionCliente":
                        mensaje_desconexion = SerializeHelper.serializar(True, "SERVIDOR_DESCONECTADO", {"motivo": "Conexión cerrada por el servidor"}).decode()
                        self.callback_mensaje(mensaje_desconexion)
                    break
                self.logger.info(f"[DEBUG] Datos recibidos: {data}")
                mensaje = data.decode()
                self.logger.info(f"[DEBUG] Mensaje decodificado: '{mensaje}'")
                
                if mensaje == "HEARTBEAT": #solo es heartbeat en servidor y en replica
                    self.logger.info(f"[DEBUG] HEARTBEAT detectado, actualizando timestamp")
                    self.timestamp = datetime.now(UTC)
                    self.conectado = True

                if self.callback_mensaje is not None:
                    self.logger.info(f"[DEBUG] Llamando callback con mensaje: '{mensaje}'")
                    self.callback_mensaje(mensaje)#self.callback_mensaje(mensaje, conn)
                else:
                    self.logger.warning(f"[DEBUG] No hay callback configurado para procesar: '{mensaje}'")
            except Exception as e:
                self.logger.error(f"Error en recepcion de mensaje: {e}")
                # Notificar error de conexión al cliente
                if self.callback_mensaje and self.tipo_nodo == "SesionCliente":
                    mensaje_desconexion = SerializeHelper.serializar(True, "SERVIDOR_DESCONECTADO", {"motivo": f"Error de conexión: {str(e)}"}).decode()
                    self.callback_mensaje(mensaje_desconexion)
                import traceback
                traceback.print_exc()
                break
        
        self.logger.info(f"[DEBUG] Cerrando conexión y limpiando")
        conn.close()
        if conn in self.conexiones:
            self.conexiones.remove(conn)

    # ---------------------------
    # Enviar mensajes
    # ---------------------------
    def enviar(self, mensaje: str, conn=None):
        try:
            if not isinstance(mensaje, bytes):
                data = mensaje.encode()  # si el mensaje no esta codificado, lo codifica
            else:
                data = mensaje
            if conn:
                conn.sendall(data)
            else:
                # broadcast si no se especifica conexión
                for c in list(self.conexiones):
                    if c.fileno() == -1:#revisar si corresponde
                        self.logger.warning("Socket cerrado detectado antes de enviar, eliminando")
                        self.conexiones.remove(c)
                        continue
                    try:
                        self.logger.warning(f"conexiones antes de hacer sendall: {self.conexiones}")
                        import traceback
                        traceback.print_exc()
                        c.sendall(data)
                        self.logger.warning(f"conexiones luego de hacer sendall: {self.conexiones}")
                    except Exception as e:
                        self.logger.warning(f"Conexión rota, motivo: {e}")
                        #falta un self.conexiones[c].cerrar() o socket close
                        import traceback
                        traceback.print_exc()
                        self.conexiones.remove(c)
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje: {e}")

    # ---------------------------
    # Heartbeat de cliente a replica
    # ---------------------------
    def _enviar_heartbeat(self):
        # Esperar a que haya al menos una conexión antes de empezar
        self.logger.info("Hilo heartbeat iniciado, esperando conexiones...")
        wait_count = 0
        while self._escuchando and not self.conexiones:
            wait_count += 1
            self.logger.info(f"[DEBUG] Esperando conexiones... intento {wait_count}, conexiones actuales: {len(self.conexiones)}")
            time.sleep(0.5)  # Esperar medio segundo y volver a verificar
            if wait_count > 20:  # Timeout después de 10 segundos
                self.logger.warning("Timeout esperando conexiones para heartbeat")
                return
        
        if not self._escuchando:
            self.logger.warning("Hilo heartbeat terminado - _escuchando es False")
            return
            
        self.logger.info(f"Conexiones detectadas ({len(self.conexiones)}), iniciando envío de heartbeats")
        
        while self._escuchando:
            self.logger.warning("*** ENVIANDO HEARTBEAT *** ...")
            current_connections = list(self.conexiones)  # Snapshot de conexiones
            self.logger.warning(f"[DEBUG] Conexiones disponibles para heartbeat: {len(current_connections)}")
            
            if current_connections:
                # Enviar heartbeat a cada conexión específicamente
                for conn in current_connections:
                    try:
                        if conn.fileno() != -1:
                            peer = conn.getpeername()
                            self.logger.info(f"[DEBUG] Enviando HEARTBEAT a conexión específica: {peer}")
                            conn.sendall(b"HEARTBEAT")
                        else:
                            self.logger.warning("Conexión cerrada detectada durante heartbeat")
                            if conn in self.conexiones:
                                self.conexiones.remove(conn)
                    except Exception as e:
                        self.logger.error(f"Error enviando heartbeat a conexión específica: {e}")
                        if conn in self.conexiones:
                            self.conexiones.remove(conn)
            else:
                self.logger.warning("No hay conexiones disponibles para enviar heartbeat - reiniciando espera")
                # Si perdimos todas las conexiones, esperar a que vuelvan
                wait_count = 0
                while self._escuchando and not self.conexiones and wait_count < 10:
                    wait_count += 1
                    self.logger.info(f"[DEBUG] Reesperando conexiones... intento {wait_count}")
                    time.sleep(0.5)
                # Si recuperamos conexiones, notificar reconexión
                if self.conexiones and self.callback_mensaje and self.tipo_nodo == "SesionCliente":
                    self.logger.info("✅ Conexiones restauradas - notificando reconexión")
                    mensaje_restauracion = SerializeHelper.serializar(True, "CONEXION_RESTAURADA", {"mensaje": "Conexión de socket restaurada"}).decode()
                    self.callback_mensaje(mensaje_restauracion)
            time.sleep(2)

    def esta_vivo(self) -> bool:
        if not self.conectado:
            return False
        if not self.timestamp:
            return False
        return datetime.now(UTC) - self.timestamp < timedelta(seconds=5)

    def cerrar(self):
        self.logger.info("Cerrando manejador de socket...")
        self._escuchando = False

        for conn in self.conexiones:
            try:
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
            except Exception as e:
                self.logger.warning(f"Error al cerrar conexión: {e}")
        self.conexiones.clear()

        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except Exception as e:
                self.logger.warning(f"Error al cerrar socket principal: {e}")
            finally:
                self.socket = None
