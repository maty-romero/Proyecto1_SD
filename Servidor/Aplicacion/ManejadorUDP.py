import socket, threading, time, json

from Servidor.Aplicacion import NodoReplica
from Utils.ConsoleLogger import ConsoleLogger


class ManejadorUDP:
    def __init__(self, owner, puerto_local, ping_interval=5, ping_timeout=10):
        self.owner: NodoReplica = owner
        self.es_productor = None
        self.puerto_local = puerto_local
        self.evento_stop = threading.Event() #flag para parar evento
        self.intervalo_ping = ping_interval
        self.ping_timeout = ping_timeout
        #es el socket para la escucha
        self.socket_local = None
        self.logger = ConsoleLogger(name="ServicioComunicacion", level="INFO")

    #Se considera que no es productor, de lo contrario se especifica ip y puerto destino para el heart
    def iniciar_socket(self,es_productor):
        self.es_productor = es_productor
        if self.evento_stop:
            self.evento_stop.clear()
        self.socket_local = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_local.bind(("0.0.0.0", self.puerto_local))
        threading.Thread(target= self.escuchar, daemon=True).start()
        if self.es_productor:
            threading.Thread(target=self._enviar_heartbeat, daemon=True).start()
        #print(f"[ManejadorUDP] iniciado en puerto {self.puerto_local}")

    def parar_escucha(self):
        self.logger.warning("Parando escucha...")
        self.evento_stop.set()
        if self.socket_local:
            self.socket_local.close()

    def escuchar(self):
        #----------------------------prueba de escucha modificada--------------------------------#
        #no se corta la escucha, asumimos que siempre van a quedarse escuchando los nodos, porque si no, pueden estar vivos, pero rechazar un ping
        while not self.evento_stop.is_set():
            self.logger.info("Escuchando")
            try:
                data, addr = self.socket_local.recvfrom(1024)
                mensaje = json.loads(data.decode())
                # Procesar mensaje en hilo separado
                threading.Thread(target=self.owner.callback_mensaje, args=(mensaje,), daemon=True).start()
                #self.owner.callback_mensaje(mensaje)
            except (socket.gaierror, ConnectionRefusedError,ConnectionResetError, OSError):
                self.logger.error("Error escuchando, continua la ejecucion...")

    #cambiamos id por 
    #el payload lo podemos utilizar para adjuntar los datos de la bd en el mensaje de envio
    def enviar_mensaje(self, ip_destino, puerto_destino, message_type, payload=None):
        self.logger.warning(f"enviando mensaje a ip {ip_destino} y puerto {puerto_destino}")
        msg = {"type": message_type, "from": self.owner.id ,"ip":self.owner.host,"puerto":self.owner.puerto}
        if payload:
            msg.update(payload)
        try:
            self.socket_local.sendto(json.dumps(msg).encode(),(ip_destino, puerto_destino))
        except:
            pass


    """Version previa, funciona"""
    def _enviar_heartbeat(self):
        """"""
        self.logger.info(f"[{self.owner.id}] intenta HEARTBEAT")

        #prueba de heart
        while not self.evento_stop.is_set():
            time.sleep(self.intervalo_ping)
            if self.owner.nodoSiguiente:

                self.logger.info(f"enviando ping a [{self.owner.nodoSiguiente.id}]{self.owner.nodoSiguiente.host}:{self.owner.nodoSiguiente.puerto}")
                ping_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                iptemp="127.0.0.1"
                ping_sock.bind((iptemp, 0))  # Puerto 0 = asignar automáticamente puerto
                puerto_asignado = ping_sock.getsockname()[1]
                ping_sock.settimeout(self.ping_timeout)
                try: 
                    msg = json.dumps({"type": "PING", "from": self.owner.id ,"ip":iptemp,"puerto":puerto_asignado}).encode()
                    ping_sock.sendto(msg, (self.owner.nodoSiguiente.host, self.owner.nodoSiguiente.puerto))
                    ping_sock.recvfrom(1024) # Esperar PONG
                except (socket.timeout, socket.gaierror, ConnectionRefusedError,ConnectionResetError, OSError):
                    print(f"No se recibio el PONG en {self.owner.id}")
                    if hasattr(self.owner, "nuevo_Siguiente"):
                        self.owner.nuevo_Siguiente()
                        break
                finally:
                    ping_sock.close()

    def ping_directo(self, nodo, timeout=2.0):
        """Verifica si un nodo está vivo enviando un PING directo"""
        try:
            ping_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ping_sock.bind(("127.0.0.1", 0))  # Puerto automático
            puerto_asignado = ping_sock.getsockname()[1]
            ping_sock.settimeout(timeout)
            
            msg = json.dumps({
                "type": "PING", 
                "from": self.owner.id,
                "ip": "127.0.0.1",
                "puerto": puerto_asignado
            }).encode()
            
            ping_sock.sendto(msg, (nodo.host, nodo.puerto))
            ping_sock.recvfrom(1024)  # Esperar PONG

            self.logger.info(f"[{self.owner.id}] ✓ {nodo.id} está vivo")
            return True
            
        except (socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError):
            self.logger.error(f"[{self.owner.id}] ✓ {nodo.id} está vivo")
            return False
            
        finally:
            ping_sock.close()