# manejador_udp_simple.py
import socket, threading, time, json

class NodoInfo:
    def __init__(self, node_id, nombre, host, puerto, esCoordinador=False):
        self.id = node_id
        self.nombre = nombre
        self.host = host
        self.puerto = puerto
        self.esCoordinador = esCoordinador


class ManejadorUDP:
    def __init__(self, owner, productor=True, puerto_local=9090, ping_interval=3, ping_timeout=1, retries=2):
        self.owner = owner
        self.es_productor = productor
        self.puerto_local = puerto_local

        self.socket_local = None
        self._stop_event = threading.Event()
        self.nodoSiguiente = None
        self.nodoAnterior = None

        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.retries = retries

    def asignar_nodo_siguiente(self, nodo):
        self.nodoSiguiente = nodo

    def asignar_nodo_anterior(self, nodo):
        self.nodoAnterior = nodo

    def iniciar_socket(self):
        self.socket_local = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_local.bind(("0.0.0.0", self.puerto_local))
        threading.Thread(target=self.escuchar, daemon=True).start()
        if self.es_productor:
            threading.Thread(target=self._enviar_heartbeat, daemon=True).start()
        print(f"[ManejadorUDP] iniciado en puerto {self.puerto_local}")

    def cerrar(self):
        self._stop_event.set()
        if self.socket_local:
            self.socket_local.close()

    def escuchar(self):
        sock = self.socket_local
        if not sock:
            return
        sock.settimeout(1)
        while not self._stop_event.is_set():
            try:
                data, addr = sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                # Esto ocurre si el socket fue cerrado desde otro hilo --> Sistema operativo
                print("socket fue cerrado desde otro hilo")
                break
            try:
                mensaje = json.loads(data.decode())
            except:
                continue
            # Procesar mensaje en hilo separado
            threading.Thread(target=self.owner.callback_mensaje, args=(mensaje,), daemon=True).start()

    def enviar_mensaje(self, dest_id, message_type, payload=None):
        target = None
        for n in self.owner.lista_nodos:
            if n.id == dest_id:
                target = (n.host, n.puerto)
                break
        if not target:
            return
        msg = {"type": message_type, "from": self.owner.id}
        if payload:
            msg.update(payload)
        try:
            self.socket_local.sendto(json.dumps(msg).encode(), target)
        except:
            pass

    def _enviar_heartbeat(self):
        sock = self.socket_local
        while not self._stop_event.is_set():
            time.sleep(self.ping_interval)
            if not self.nodoSiguiente:
                continue
            alive = False
            for _ in range(self.retries):
                try:
                    self.enviar_mensaje(self.nodoSiguiente.id, "PING")
                    sock.settimeout(self.ping_timeout)
                    data, addr = sock.recvfrom(4096)
                    resp = json.loads(data.decode())
                    if resp.get("type") == "PONG":
                        alive = True
                        break
                except:
                    continue
            if not alive:
                if hasattr(self.owner, "on_siguiente_muerto"):
                    self.owner.on_siguiente_muerto(self.nodoSiguiente)


# ---------- NodoReplica ----------
class NodoReplica:
    def __init__(self, node_id, nombre, host, puerto, lista_nodos):
        self.id = node_id
        self.nombre = nombre
        self.host = host
        self.puerto = puerto
        self.lista_nodos = lista_nodos
        self.esCoordinador = False
        self.manejador = ManejadorUDP(self, True, self.puerto)
        self.recalcular_vecinos()

    def start(self):
        self.manejador.iniciar_socket()

    def recalcular_vecinos(self):
        ids = [n.id for n in self.lista_nodos]
        if self.id not in ids:
            self.manejador.asignar_nodo_siguiente(None)
            return
        idx = ids.index(self.id)
        siguiente = self.lista_nodos[idx + 1] if idx + 1 < len(self.lista_nodos) else None
        self.manejador.asignar_nodo_siguiente(siguiente)
        print(f"[{self.id}] siguiente = {siguiente.id if siguiente else 'NINGUNO'}")

    def callback_mensaje(self, mensaje):
        tipo = mensaje.get("type")
        sender = mensaje.get("from")
        if tipo == "PING":
            print(f"[{self.id}] Recibió PING de {sender}")
            self.manejador.enviar_mensaje(sender, "PONG")
        elif tipo == "PONG":
            print(f"[{self.id}] Recibió PONG de {sender}")

    def on_siguiente_muerto(self, dead_node):
        print(f"[{self.id}] Siguiente muerto detectado: {dead_node.id}")
        self.manejador.asignar_nodo_siguiente(None)
        self.esCoordinador = True
        print(f"[{self.id}] Me proclamo COORDINADOR")


if __name__ == "__main__":
    nodo1 = NodoInfo(1, "Nodo1", "127.0.0.1", 10001)
    nodo2 = NodoInfo(2, "Nodo2", "127.0.0.1", 10002)
    nodo3 = NodoInfo(3, "Nodo3", "127.0.0.1", 10003)

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
        app2.manejador.cerrar()
        time.sleep(10)

        print("\n--- Estado final ---")
        print(f"Nodo1 coordinador: {app1.esCoordinador}, siguiente: {app1.manejador.nodoSiguiente}")
        print(f"Nodo3 coordinador: {app3.esCoordinador}, siguiente: {app3.manejador.nodoSiguiente}")

        time.sleep(10)
    except KeyboardInterrupt:
        print("Deteniendo demo...")

    app1.manejador.cerrar()
    app2.manejador.cerrar()
    app3.manejador.cerrar()