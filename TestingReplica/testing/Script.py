# manejador_udp_simple.py
import socket, threading, time, json

class ManejadorUDP:
    def __init__(self, owner, puerto_local, ping_interval=3, ping_timeout=9, retries=2):
        self.owner: NodoReplica = owner
        self.es_productor = None
        self.puerto_local = puerto_local
        self.evento_stop = threading.Event() #flag para parar evento
        #self.nodoSiguiente:Nodo = nodoSiguiente
        #self.nodoAnterior:Nodo = nodoAnterior
        self.intervalo_ping = ping_interval
        self.ping_timeout = ping_timeout
        self.retries = retries
        #es el socket para la escucha
        self.socket_local = None
    

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
        print("Parando escucha...")
        self.evento_stop.set()
        if self.socket_local:
            self.socket_local.close()

    def escuchar(self):
        #----------------------------prueba de escucha modificada--------------------------------#
        #no se corta la escucha, asumimos que siempre van a quedarse escuchando los nodos, porque si no, pueden estar vivos, pero rechazar un ping
        while not self.evento_stop.is_set():
            print("escuchando")
            try:
                data, addr = self.socket_local.recvfrom(1024)
                mensaje = json.loads(data.decode())
                # Procesar mensaje en hilo separado
                #threading.Thread(target=self.owner.callback_mensaje, args=(mensaje,), daemon=True).start()
                self.owner.callback_mensaje(mensaje)
            except (socket.gaierror, ConnectionRefusedError,ConnectionResetError, OSError):
                print(f"[Manejador] Error escuchando, continua la ejecucion...")

    #cambiamos id por 
    #el payload lo podemos utilizar para adjuntar los datos de la bd en el mensaje de envio
    def enviar_mensaje(self, ip_destino, puerto_destino, message_type, payload=None):
        print(f"enviando mensaje a ip {ip_destino} y puerto {puerto_destino}")
        msg = {"type": message_type, "from": self.owner.id ,"ip":self.owner.host,"puerto":self.owner.puerto}
        if payload:
            msg.update(payload)
        try:
            self.socket_local.sendto(json.dumps(msg).encode(),(ip_destino, puerto_destino))
        except:
            pass

    # def _enviar_heartbeat(self):
    #     """Envía heartbeats periódicos al nodo siguiente"""
    #     print(f"[{self.owner.id}] Iniciando heartbeat thread")
        
    #     while not self.evento_stop.is_set():
    #         time.sleep(self.intervalo_ping)
            
    #         if self.owner.nodoSiguiente:
    #             print(f"[{self.owner.id}] Enviando ping a [{self.owner.nodoSiguiente.id}] {self.owner.nodoSiguiente.host}:{self.owner.nodoSiguiente.puerto}")

    #             ping_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #             ping_sock.bind(("0.0.0.0", 0))  # Puerto 0 = asignar automáticamente puerto
    #             puerto_asignado = ping_sock.getsockname()[1]
    #             try: 
    #                 msg = json.dumps({
    #                     "type": "PING", 
    #                     "from": self.owner.id,
    #                     "ip": "127.0.0.1",  # o self.owner.host si lo tienes
    #                     "puerto": puerto_asignado
    #                 }).encode()
                    
    #                 ping_sock.sendto(msg, (self.owner.nodoSiguiente.host, self.owner.nodoSiguiente.puerto))
    #                 data, addr = ping_sock.recvfrom(1024)  # Esperar PONG
    #                 print(f"[{self.owner.id}] ✓ PONG recibido")
                    
    #             except socket.timeout:
    #                 print(f"[{self.owner.id}] ✗ Timeout - No se recibió PONG")
    #                 self.owner.nuevo_Siguiente()
    #                 break
                    
    #             except (socket.gaierror, ConnectionRefusedError, ConnectionResetError, OSError) as e:
    #                 print(f"[{self.owner.id}] ✗ Error de conexión: {e}")
    #                 self.owner.nuevo_Siguiente()
    #                 break
                    
    #             except Exception as e:
    #                 print(f"[{self.owner.id}] ✗ Error inesperado: {e}")
    #                 self.owner.nuevo_Siguiente()
    #                 break
                    
    #             finally:
    #                 ping_sock.close()
    #         else:
    #             print(f"[{self.owner.id}] No hay nodoSiguiente configurado")
        
    #     print(f"[{self.owner.id}] Heartbeat thread terminado")


    """Version previa, funciona"""
    def _enviar_heartbeat(self):
        """"""
        print("intenta HEART")
        #prueba de heart
        while not self.evento_stop.is_set():
            time.sleep(self.intervalo_ping)
            if self.owner.nodoSiguiente:
                print(f"enviando ping a [{self.owner.nodoSiguiente.id}]{self.owner.nodoSiguiente.host}:{self.owner.nodoSiguiente.puerto}")
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
                    if hasattr(self.owner, "on_siguiente_muerto"):
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
            
            print(f"[{self.owner.id}] ✓ {nodo.id} está vivo")
            return True
            
        except (socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError):
            print(f"[{self.owner.id}] ✗ {nodo.id} no respondió")
            return False
            
        finally:
            ping_sock.close()

class Nodo:
    def __init__(self, id_nodo, nombre, host, puerto, esCoordinador=False):
        self.id = id_nodo
        self.nombre = nombre
        self.host = host
        self.puerto = puerto
        self.esCoordinador = esCoordinador

# ---------- NodoReplica ----------
class NodoReplica(Nodo):
    def __init__(self, id_nodo, nombre, host, puerto, lista_nodos,esCoordinador=False):
        super().__init__(id_nodo, nombre, host, puerto, esCoordinador)
        self.puerto = puerto
        self.lista_nodos = lista_nodos
        self.nodoSiguiente: Nodo = None
        self.nodoAnterior: Nodo = None
        self.recalcular_vecinos()
        #se envia ip y puerto de siguiente, ver como reasignar...
        self.manejador = ManejadorUDP(self, self.puerto)
         # Variables para verificar si un nodo está vivo
        
        #hilo de prueba
        if self.esCoordinador:
            threading.Thread(target= self.broadcast_datos_DB, daemon=True).start()
        
    def broadcast_datos_DB(self):
        while True:
            time.sleep(5)
            # Buscar todos los nodos con ID menor al mío
            nodos_menores = [n for n in self.lista_nodos if n.id < self.id]
            
            if not nodos_menores:
                print(f"[{self.id}] No hay nodos menores para notificar")
                return
            
            # Enviar mensaje a cada nodo menor
            for nodo in nodos_menores:
                print(f"[{self.id}] Enviando ACTUALIZAR_DB a nodo {nodo.id}")
                self.manejador.enviar_mensaje(
                    nodo.host,
                    nodo.puerto,
                    "ACTUALIZAR_DB"
                )
            
            print(f"[{self.id}] Notificación completada a {len(nodos_menores)} nodos")


    def iniciar(self):
        if self.esCoordinador:
            #Si el nodo es el coordinador, no envia heart ni hay nodoSiguiente
            #False, no es productor
            self.manejador.iniciar_socket(es_productor=not self.esCoordinador)
        else:
            #True, es productor
            self.manejador.iniciar_socket(es_productor=not self.esCoordinador)
            
    def asignar_nodo_siguiente(self, nodo):
        self.nodoSiguiente = nodo

    def asignar_nodo_anterior(self, nodo):
        self.nodoAnterior = nodo

    def recalcular_vecinos(self):
        ids = [n.id for n in self.lista_nodos]
        idx = ids.index(self.id)

        # Siguiente nodo
        siguiente = self.lista_nodos[idx + 1] if idx + 1 < len(self.lista_nodos) else None
        self.asignar_nodo_siguiente(siguiente)

        # Nodo anterior
        anterior = self.lista_nodos[idx - 1] if idx > 0 else None
        self.asignar_nodo_anterior(anterior)

        print(f"[{self.id}] siguiente = {siguiente.id if siguiente else 'NINGUNO'}, anterior = {anterior.id if anterior else 'NINGUNO'}")

    def callback_mensaje(self, mensaje):
        
        tipo = mensaje.get("type")
        sender = mensaje.get("from")
        ip = mensaje.get("ip")
        puerto = mensaje.get("puerto")

        print(f"[Nodo {self.id}] MENSAJE RECIBIDO: TYPE: {mensaje}, FROM: {sender}" )
        if tipo == "PING":
            try:
                #le tiene que responder al anterior, osea a dos
                print(f"[{self.id}] Recibió PING de {sender}")
                print(f"Enviando PONG a ANTERIOR: {self.nodoAnterior.id}, IP:{ip}, Puerto: {puerto}")
                self.manejador.enviar_mensaje(ip,puerto,"PONG")
            except Exception as e: 
                print(f"Error al enviar PONG: {e}")
        elif tipo == "NUEVO_ANTERIOR":
            self.nuevo_anterior(sender,ip,puerto)
        
        elif tipo == "ACK_NUEVO_ANTERIOR":
            print(f"[{self.id}] Reconexión exitosa con {sender}")

        elif tipo == "ACTUALIZAR_DB":
            print(f"[{self.id}] Solicitud de actualización de DB desde nodo [{sender}]")
            #self.actualizar_db(datos)
            pass



        # elif tipo == "PONG":
        #     print(f"[{self.id}] Recibió PONG de {sender}")
    

    def on_siguiente_muerto(self):
        print(f"[{self.id}] Siguiente muerto detectado: {self.nodoSiguiente.id if self.nodoSiguiente else 'NINGUNO'}")
        self.nodoSiguiente = None

        #candidatos = sorted([n for n in self.lista_nodos if n.id > self.id], key=lambda n: n.id)
        # nuevo_siguiente = None

        # # for cand in candidatos:
        # #     #msg = {"type": "ESTAS_VIVO", "from": self.cand.id}
        # #     if self.manejador.enviar_mensaje(cand.host, cand.puerto, "ESTAS_VIVO"):
        # #         nuevo_siguiente = cand
        # #         break

        # if nuevo_siguiente:
        #     print(f"[{self.id}] Nuevo siguiente encontrado: {nuevo_siguiente.id}")
        #     self.nodoSiguiente = nuevo_siguiente
        #     self.esCoordinador = False
        # else:
        #     print(f"[{self.id}] No hay siguiente vivo -> me proclamo COORDINADOR")
        #     self.esCoordinador = True

        # print(f"MANEJADOR: {self.manejador}")
        # # reiniciar manejador sin crear uno nuevo
        # if self.manejador:
        #     self.manejador.parar_escucha()  # detener socket y threads
        #     self.iniciar()  # reiniciar correctamente
        
    def nuevo_Siguiente(self):
        """Busca un nuevo nodo siguiente cuando el actual falla"""
        nodo_caido = self.nodoSiguiente
        print(f"[{self.id}] Nodo siguiente caído: {nodo_caido.id if nodo_caido else 'NINGUNO'}")
        
        # Buscar candidatos con ID mayor
        candidatos = [n for n in self.lista_nodos if n.id > self.id and n.id != (nodo_caido.id if nodo_caido else -1)]
        
        nuevo_sig = None
        for cand in candidatos:
            print(f"[{self.id}] Probando candidato {cand.id}...")
            if self.manejador.ping_directo(cand):
                nuevo_sig = cand
                break
        
        if nuevo_sig:
            # Asignar nuevo siguiente
            self.asignar_nodo_siguiente(nuevo_sig)
            self.esCoordinador = False
            print(f"[{self.id}] Nuevo siguiente: {nuevo_sig.id}")
            
            # Notificar al nuevo siguiente
            self.manejador.enviar_mensaje(
                nuevo_sig.host, nuevo_sig.puerto, "NUEVO_ANTERIOR",
                {"nodo_anterior_id": self.id, "host": self.host, "puerto": self.puerto}
            )
            
            # Reiniciar manejador
            self.manejador.parar_escucha()
            time.sleep(0.5)
            self.iniciar()
        else:
            # Soy coordinador
            print(f"[{self.id}] No hay más nodos vivos -> COORDINADOR")
            self.asignar_nodo_siguiente(None)
            self.esCoordinador = True
            self.manejador.parar_escucha()
            time.sleep(0.5)
            self.iniciar()
            self.levantar_nuevo_coordinador()   

    def nuevo_anterior(self, nodo_anterior_id, host, puerto):
        """
        Asigna un nuevo nodo anterior cuando el nodo que me precedía detectó
        la falla de su siguiente (que era mi anterior).
        
        Args:
            nodo_anterior_id: ID del nuevo nodo anterior
            host: IP del nuevo nodo anterior
            puerto: Puerto del nuevo nodo anterior
        """
        print(f"[{self.id}] Asignando nuevo nodo anterior: {nodo_anterior_id}")
        
        # Buscar el nodo en la lista existente
        nuevo_ant = None
        for n in self.lista_nodos:
            if n.id == nodo_anterior_id:
                nuevo_ant = n
                break
        
        # Si no está en la lista, crear referencia temporal
        if not nuevo_ant:
            nuevo_ant = Nodo(nodo_anterior_id, f"Nodo-{nodo_anterior_id}", host, puerto)
            print(f"[{self.id}] Nodo anterior no estaba en lista, creando referencia temporal")
        
        self.asignar_nodo_anterior(nuevo_ant)
        print(f"[{self.id}] ✓ Nuevo anterior asignado: {nuevo_ant.id}")
        
        # Enviar confirmación
        self.manejador.enviar_mensaje(
            nuevo_ant.host,
            nuevo_ant.puerto,
            "ACK_NUEVO_ANTERIOR"
        )

    def levantar_nuevo_coordinador(self):
        """
        Se invoca cuando este nodo se convierte en coordinador.
        Implementación futura: inicializar servicios de coordinación, etc.
        """
        print(f"[{self.id}] ==========================================")
        print(f"[{self.id}] ME PROCLAMO NUEVO COORDINADOR")
        print(f"[{self.id}] ==========================================")
        threading.Thread(target= self.broadcast_datos_DB, daemon=True).start()
        # TODO: Implementar lógica de coordinador
        pass