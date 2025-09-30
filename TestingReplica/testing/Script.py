# manejador_udp_simple.py
import socket, threading, time, json

class ManejadorUDP:
    def __init__(self, owner, puerto_local=9090, ping_interval=1, ping_timeout=8, retries=2):
        self.owner = owner
        self.es_productor = None
        self.puerto_local = puerto_local

        self.socket_local = None
        self.evento_stop = threading.Event() #flag para parar evento
        #self.nodoSiguiente = None
        #self.nodoAnterior = None

        self.intervalo_ping = ping_interval
        self.ping_timeout = ping_timeout
        self.retries = retries

    # def asignar_nodo_siguiente(self, nodo):
    #     self.nodoSiguiente = nodo

    # def asignar_nodo_anterior(self, nodo):
    #     self.nodoAnterior = nodo

    #Se considera que no es productor, de lo contrario se especifica ip y puerto destino para el heart
    def iniciar_socket(self,es_productor=False,ip_destino=None,puerto_destino=None):
        self.es_productor = es_productor
        if self.evento_stop:
            self.evento_stop.clear()
        self.socket_local = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_local.bind(("0.0.0.0", self.puerto_local))
        threading.Thread(target=self.escuchar, daemon=True).start()
        if self.es_productor and ip_destino and puerto_destino:
            threading.Thread(target=self._enviar_heartbeat(ip_destino,puerto_destino), daemon=True).start()
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


        # sock = self.socket_local
        # if not sock:
        #     return
        # sock.settimeout(1)
        # while not self._stop_event.is_set():
        #     try:
        #         data, addr = sock.recvfrom(4096)
        #     except socket.timeout:
        #         continue
        #     except OSError:
        #         # Esto ocurre si el socket fue cerrado desde otro hilo --> Sistema operativo
        #         print("socket fue cerrado desde otro hilo")
        #         break
        #     try:
        #         mensaje = json.loads(data.decode())
        #     except:
        #         continue
        #     # Procesar mensaje en hilo separado
        #     threading.Thread(target=self.owner.callback_mensaje, args=(mensaje,), daemon=True).start()

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

    def _enviar_heartbeat(self,ip_destino,puerto_destino):
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
                self.enviar_mensaje(ip_destino,puerto_destino, "PING")
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
        # while not self.evento_stop.is_set():
            
        #     time.sleep(self.intervalo_ping)
        #     #si no hay nodo siguiente para enviar mensaje, continue, o cerrar hilo a lo mejor
        #     if not self.nodoSiguiente:
        #         continue
        #     ping_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #     alive = False
        #     for _ in range(self.retries):
        #         try:
        #             self.enviar_mensaje(self.nodoSiguiente.id, "PING")
        #             ping_sock.settimeout(self.ping_timeout)
        #             data, addr = ping_sock.recvfrom(4096)
        #             resp = json.loads(data.decode())
        #             if resp.get("type") == "PONG":
        #                 alive = True
        #                 break
        #         except:
        #             continue
        #     if not alive:
        #         if hasattr(self.owner, "on_siguiente_muerto"):
        #             self.owner.on_siguiente_muerto(self.nodoSiguiente)

class Nodo:
    def __init__(self, id_nodo, nombre, host, puerto, esCoordinador=False):
        self.id = id_nodo
        self.nombre = nombre
        self.host = host
        self.puerto = puerto
        self.esCoordinador = esCoordinador

# ---------- NodoReplica ----------
class NodoReplica(Nodo):
    def __init__(self, id_nodo, nombre, host, puerto, lista_nodos):
        super().__init__(id_nodo,nombre,host,puerto)
        self.lista_nodos = lista_nodos
        self.nodoSiguiente: Nodo = None
        self.nodoAnterior: Nodo = None
        self.recalcular_vecinos()
        #se envia ip y puerto de siguiente, ver como reasignar...
        self.manejador = ManejadorUDP(self, self.puerto)

    def start(self):
        if self.esCoordinador:
            #Si el nodo es el coordinador, no envia heart ni hay nodoSiguiente
            self.manejador.iniciar_socket()
        else:
            self.manejador.iniciar_socket(True,self.nodoSiguiente.host,self.nodoSiguiente.puerto)
            

    def asignar_nodo_siguiente(self, nodo):
        self.nodoSiguiente = nodo

    def asignar_nodo_anterior(self, nodo):
        self.nodoAnterior = nodo


    def recalcular_vecinos(self):
        ids = [n.id for n in self.lista_nodos]
        if self.id not in ids:
            self.asignar_nodo_siguiente(None)
            return
        idx = ids.index(self.id)
        siguiente = self.lista_nodos[idx + 1] if idx + 1 < len(self.lista_nodos) else None
        self.asignar_nodo_siguiente(siguiente)
        print(f"[{self.id}] siguiente = {siguiente.id if siguiente else 'NINGUNO'}")

    def callback_mensaje(self, mensaje):
        tipo = mensaje.get("type")
        sender = mensaje.get("from")
        if tipo == "PING":
            #le tiene que responder al siguiente
            print(f"[{self.id}] Recibió PING de {sender}")
            self.manejador.enviar_mensaje(self.nodoSiguiente.host,self.nodoSiguiente.puerto,"PONG")
        elif tipo == "PONG":
            print(f"[{self.id}] Recibió PONG de {sender}")

    def on_siguiente_muerto(self):
        print(f"[{self.id}] Siguiente muerto detectado: {self.nodoSiguiente.id}")
        self.asignar_nodo_siguiente(None)
        self.manejador = self.manejador = ManejadorUDP(self, False, self.puerto)
        self.manejador.iniciar_socket()
        self.esCoordinador = True
        print(f"[{self.id}] Me proclamo COORDINADOR")


if __name__ == "__main__":
    nodo1 = Nodo(1, "Nodo1", "127.0.0.1", 10001)
    nodo2 = Nodo(2, "Nodo2", "127.0.0.1", 10002)
    nodo3 = Nodo(3, "Nodo3", "127.0.0.1", 10003,True)

    lista_nodos = [nodo1, nodo2, nodo3]

    app1 = NodoReplica(1, "Nodo1", "127.0.0.1", 10001, lista_nodos)
    app2 = NodoReplica(2, "Nodo2", "127.0.0.1", 10002, lista_nodos)
    app3 = NodoReplica(3, "Nodo3", "127.0.0.1", 10003, lista_nodos)

    app1.start()
    app2.start()
    app3.start()

    print("Script corriendo... Ctrl+C para detener")

    try:
        time.sleep(10)
        print("\n--- Simulando caída de Nodo2 ---")
        app2.manejador.parar_escucha()
        time.sleep(10)

        print("\n--- Estado final ---")
        print(f"Nodo1 coordinador: {app1.esCoordinador}, siguiente: {app1.manejador.nodoSiguiente}")
        print(f"Nodo3 coordinador: {app3.esCoordinador}, siguiente: {app3.manejador.nodoSiguiente}")

        time.sleep(10)
    except KeyboardInterrupt:
        print("Deteniendo demo...")

    app1.manejador.parar_escucha()
    app2.manejador.parar_escucha()
    app3.manejador.parar_escucha()