# manejador_udp_simple.py
import socket, threading, time, json

class ManejadorUDP:
    def __init__(self, owner,nodoAnterior, puerto_local=9090, ping_interval=1, ping_timeout=8, retries=2):
        self.owner: NodoReplica = owner
        self.es_productor = None
        self.puerto_local = puerto_local

        self.socket_local = None
        self.evento_stop = threading.Event() #flag para parar evento
        #self.nodoSiguiente:Nodo = nodoSiguiente
        self.nodoAnterior:Nodo = nodoAnterior

        self.intervalo_ping = ping_interval
        self.ping_timeout = ping_timeout
        self.retries = retries

    # def asignar_nodo_siguiente(self, nodo):
    #     self.nodoSiguiente = nodo

    # def asignar_nodo_anterior(self, nodo):
    #     self.nodoAnterior = nodo

    #Se considera que no es productor, de lo contrario se especifica ip y puerto destino para el heart
    def iniciar_socket(self,es_productor):
        self.es_productor = es_productor
        print(f"es productor:{es_productor}")
        if self.evento_stop:
            print(f"self.evento_stop: {self.evento_stop}")
            self.evento_stop.clear()
        self.socket_local = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_local.bind(("0.0.0.0", self.puerto_local))
        threading.Thread(target= self.escuchar, daemon=True).start()
        if self.es_productor:
            threading.Thread(target=self._enviar_heartbeat, daemon=True).start()
        print(f"[ManejadorUDP] iniciado en puerto {self.puerto_local}")

    def parar_escucha(self):
        self.evento_stop.set()
        if self.socket_local:
            self.socket_local.close()

    def escuchar(self):
        #----------------------------prueba de escucha modificada--------------------------------#
        #no se corta la escucha, asumimos que siempre van a quedarse escuchando los nodos, porque si no, pueden estar vivos, pero rechazar un ping
        while not self.evento_stop.is_set():
            try:
                data, addr = self.socket_local.recvfrom(4096)
                mensaje = json.loads(data.decode())
                # Procesar mensaje en hilo separado
                threading.Thread(target=self.owner.callback_mensaje, args=(mensaje,), daemon=True).start()
            except Exception as e:
                print(f"[Manejador] Error escuchando: {e}")

    #cambiamos id por 
    #el payload lo podemos utilizar para adjuntar los datos de la bd en el mensaje de envio
    def enviar_mensaje(self, ip_destino, puerto_destino, message_type, payload=None):
        target = None
        #comprobacion para determinar si el id de destino esta en la lista
        # target = next(
        #     ((n.host, n.puerto) for n in self.owner.lista_nodos if n.id == ip_destino),
        #     None
        #     )
        # for n in self.owner.lista_nodos:
        #     if n.id == dest_id:
        #         target = (n.host, n.puerto)
        #         break 
        if not target:
            return
        msg = {"type": message_type, "from": self.owner.id}
        if payload:
            msg.update(payload)
        try:
            self.socket_local.sendto(json.dumps(msg).encode(), (ip_destino, puerto_destino))
        except:
            pass

    def _enviar_heartbeat(self):
        """"""
        #prueba de heart
        while not self.evento_stop.is_set():
            print("se envio heart")
            time.sleep(self.intervalo_ping)
            #si no hay nodo siguiente para enviar mensaje, continue, o cerrar hilo a lo mejor
            # if not self.nodoSiguiente:
            #     continue
            ping_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #alive = False creo que no necesitamos esto, el timeout es suficiente
            #for _ in range(self.retries):#el reintentar tampoco lo veo necesario, ya esta el sleep
            try: 
                self.enviar_mensaje(self.owner.nodoSiguiente.host ,self.owner.nodoSiguiente.puerto, "PING")
                ping_sock.settimeout(self.ping_timeout)
                data, addr = ping_sock.recvfrom(4096)
                resp = json.loads(data.decode())
                # if resp.get("type") == "PONG":
                #     alive = True
                #     break
            except (socket.timeout, socket.gaierror):
                    if hasattr(self.owner, "on_siguiente_muerto"):
                        self.owner.on_siguiente_muerto()
                    break
       
    def ping_directo(self, nodo, timeout=1.0):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(timeout)
            msg = json.dumps({"type": "PING", "from": self.owner.id}).encode()
            s.sendto(msg, (nodo.host, nodo.puerto))
            data, _ = s.recvfrom(4096)
            resp = json.loads(data.decode())
            return resp.get("type") == "PONG"
        except (socket.timeout, OSError, json.JSONDecodeError):
            return False
        finally:
            s.close()

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
        super().__init__(id_nodo,nombre,host,puerto,esCoordinador)
        self.lista_nodos = lista_nodos
        self.nodoSiguiente: Nodo = None
        self.nodoAnterior: Nodo = None
        self.recalcular_vecinos()
        #se envia ip y puerto de siguiente, ver como reasignar...
        self.manejador = ManejadorUDP(self,self.nodoAnterior, self.puerto)
        
    def iniciar(self):
        print(f"dentro del iniciar, es coordinador? :{self.esCoordinador}")
        comprobacion = self.esCoordinador
        if comprobacion:
            #Si el nodo es el coordinador, no envia heart ni hay nodoSiguiente
            #False, no es productor
            print(f"ENTRO AL IF")
            self.manejador.iniciar_socket(False)
        else:
            #True, es productor
            print(f"entro al else")
            self.manejador.iniciar_socket(True)
            
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
        if tipo == "PING":
            #le tiene que responder al siguiente
            print(f"[{self.id}] Recibió PING de {sender}")
            self.manejador.enviar_mensaje(self.nodoAnterior.host,self.nodoAnterior.puerto,"PONG")
        elif tipo == "PONG":
            print(f"[{self.id}] Recibió PONG de {sender}")

    def on_siguiente_muerto(self):
        print(f"[{self.id}] Siguiente muerto detectado: {self.nodoSiguiente.id if self.nodoSiguiente else 'NINGUNO'}")
        self.nodoSiguiente = None

        candidatos = [n for n in self.lista_nodos if n.id > self.id]
        nuevo_siguiente = None

        for cand in candidatos:
            if self.manejador.ping_directo(cand):
                nuevo_siguiente = cand
                break

        if nuevo_siguiente:
            print(f"[{self.id}] Nuevo siguiente encontrado: {nuevo_siguiente.id}")
            self.nodoSiguiente = nuevo_siguiente
            self.esCoordinador = False
        else:
            print(f"[{self.id}] No hay siguiente vivo -> me proclamo COORDINADOR")
            self.esCoordinador = True

        # reiniciar manejador sin crear uno nuevo
        if self.manejador:
            self.manejador.parar_escucha()                  # detener socket y threads
            self.manejador.iniciar_socket(es_productor=not self.esCoordinador)  # reiniciar correctamente
