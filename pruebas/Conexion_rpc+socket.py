
"""CONEXION ACTUA DE FACHADA, esta implementacion es un facade"""
# ==========================================
# protocolo.py
# ==========================================
import json

def serializar(tipo, data):
    """Serializa un mensaje en formato JSON."""
    return json.dumps({"tipo": tipo, "data": data}).encode()

def deserializar(raw_bytes):
    """Deserializa un mensaje desde JSON."""
    obj = json.loads(raw_bytes.decode())
    return obj["tipo"], obj["data"]


# ==========================================
# rpc_handler.py
# ==========================================
import Pyro5.api

class ManejadorRPC:
    def __init__(self, uri):
        """Crea un proxy RPC hacia el servidor."""
        self.proxy = Pyro5.api.Proxy(uri)

    def call(self, metodo, *args, **kwargs):
        """Llama a un método remoto vía RPC."""
        return getattr(self.proxy, metodo)(*args, **kwargs)

    def expose(self, objeto):
        """Expone un objeto local para que otros puedan invocar sus métodos."""
        daemon = Pyro5.api.Daemon()
        uri = daemon.register(objeto)
        print("Objeto RPC expuesto en:", uri)
        daemon.requestLoop()


# ==========================================
# socket_handler.py
# ==========================================
import socket, threading, json

class ManejadorSocket:
    def __init__(self, mode, addr):
        """
        mode: "server" o "client"
        addr: (host, port)
        """
        self.mode = mode
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.on_message = lambda raw, conn: None  # callback externo
        self.conexiones_activas = []

    def start(self):
        if self.mode == "server":
            self.sock.bind(self.addr)
            self.sock.listen()
            threading.Thread(target=self._accept_loop, daemon=True).start()
        else:
            self.sock.connect(self.addr)
            threading.Thread(target=self._recv_loop, args=(self.sock,), daemon=True).start()

    def send(self, data, conn=None):
        """Envía datos serializados por el socket."""
        msg = json.dumps(data).encode()
        if self.mode == "server" and conn:
            conn.sendall(msg)
        else:
            self.sock.sendall(msg)

    def _accept_loop(self):
        while True:
            conn, addr = self.sock.accept()
            self.conexiones_activas.append(conn)
            threading.Thread(target=self._recv_loop, args=(conn,), daemon=True).start()

    def _recv_loop(self, conn):
        while True:
            data = conn.recv(4096)
            if not data:
                break
            self.on_message(data, conn)


# ==========================================
# conexion_cliente.py
# ==========================================
from protocolo import serializar, deserializar
from rpc_handler import ManejadorRPC
from socket_handler import ManejadorSocket

class ConexionCliente:
    def __init__(self, addr_rpc, addr_socket):
        self.rpc = ManejadorRPC(addr_rpc)
        self.socket = ManejadorSocket("client", addr_socket)
        self.socket.on_message = self._on_message
        self.socket.start()

    # ==== Métodos para ENVIAR al servidor ====
    def enviar_join(self, nombre):
        self.rpc.call("join", {"nombre": nombre})

    def enviar_respuestas(self, respuestas):
        self.rpc.call("word", {"palabra": respuestas})

    def enviar_heartbeat(self):
        self.socket.send({"tipo": "HEARTBEAT"})

    # ==== Callbacks de RECEPCIÓN ====
    def _on_message(self, raw, conn):
        tipo, data = deserializar(raw)
        if tipo == "ROUND_START":
            print(f"Comienza la ronda con categoría: {data['categoria']}")
        elif tipo == "SCORES":
            print("Puntajes recibidos:", data)


# ==========================================
# conexion_servidor.py
# ==========================================
from protocolo import serializar, deserializar
from rpc_handler import RPCHandler
from socket_handler import ManejadorSocket

class ConexionServidor:
    def __init__(self, addr_rpc, addr_socket):
        self.rpc = ManejadorRPC(addr_rpc)
        self.socket = ManejadorSocket("server", addr_socket)
        self.socket.on_message = self._on_message
        self.socket.start()
        self.replicas = []

    # ==== Métodos para ENVIAR a clientes ====
    def broadcast(self, tipo, data):
        """Envía a todos los clientes conectados."""
        for conn in self.socket.conexiones_activas:
            self.socket.send({"tipo": tipo, "data": data}, conn)

    def enviar_a_replica(self, tipo, data):
        """Envía mensajes de sincronización a la réplica."""
        for conn in self.replicas:
            self.socket.send({"tipo": tipo, "data": data}, conn)

    # ==== Callbacks de RECEPCIÓN ====
    def _on_message(self, raw, conn):
        tipo, data = deserializar(raw)
        if tipo == "JOIN_REPLICA":
            self.replicas.append(conn)
            print("Replica conectada.")
        elif tipo == "WORD":
            self._registrar_palabra(data["palabra"], conn)
        elif tipo == "HEARTBEAT":
            self.socket.send({"tipo": "PONG"}, conn)

    # ==== Lógica de servidor ====
    def _registrar_palabra(self, palabra, conn):
        print(f"Palabra recibida de un cliente: {palabra}")
        # aquí va tu lógica para actualizar estado y reenviar a replica


import socket
import pickle
import threading
import Pyro5.api


class ConexionReplica:
    """
    Clase que maneja la comunicación entre el servidor principal y su réplica.
    Puede usar socket para replicación continua (heartbeat + eventos)
    y opcionalmente RPC para sincronizar estados completos.
    """

    def __init__(self, dir_rpc: str, dir_socket: tuple, es_servidor: bool = True):
        """
        :param dir_rpc: URI del servidor Pyro5 (para RPC entre replicas)
        :param dir_socket: (host, puerto) para socket
        :param es_servidor: True si es la réplica principal que envía datos,
                            False si es la réplica secundaria que escucha.
        """
        self.dir_rpc = dir_rpc
        self.dir_socket = dir_socket
        self.es_servidor = es_servidor
        self.rpc_proxy = None
        self.sock = None
        self.running = False

    # ---------------------------
    # Inicialización de conexiones
    # ---------------------------
    def iniciar_rpc(self):
        """Crea un proxy RPC para enviar/recibir estados completos."""
        if self.dir_rpc:
            self.rpc_proxy = Pyro5.api.Proxy(self.dir_rpc)

    def iniciar_socket(self):
        """Crea socket TCP para replicación en tiempo real."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.es_servidor:
            self.sock.bind(self.dir_socket)
            self.sock.listen(1)
            print(f"[Replica] Esperando conexión de réplica secundaria en {self.dir_socket}...")
            conn, addr = self.sock.accept()
            print(f"[Replica] Réplica secundaria conectada desde {addr}")
            self.conn = conn
        else:
            self.sock.connect(self.dir_socket)
            self.conn = self.sock

    # ---------------------------
    # Métodos de comunicación
    # ---------------------------
    def enviar_evento(self, data: dict):
        """
        Envía un evento serializado a la otra réplica.
        """
        if not hasattr(self, "conn"):
            raise RuntimeError("Conexión no inicializada")
        payload = pickle.dumps(data)
        self.conn.sendall(payload)

    def recibir_evento(self):
        """
        Recibe un evento serializado de la otra réplica.
        (bloqueante, usar en un hilo separado)
        """
        if not hasattr(self, "conn"):
            raise RuntimeError("Conexión no inicializada")
        while self.running:
            try:
                data = self.conn.recv(4096)
                if not data:
                    break
                evento = pickle.loads(data)
                self.procesar_evento(evento)
            except Exception as e:
                print(f"[Replica] Error recibiendo evento: {e}")
                break

    def procesar_evento(self, evento):
        """
        Lógica para aplicar los eventos recibidos a la réplica.
        """
        print(f"[Replica] Evento recibido: {evento}")
        # Aquí iría la lógica de actualización de la base de datos
        # o del estado del servidor réplica.

    # ---------------------------
    # Ejecución
    # ---------------------------
    def iniciar(self):
        """Inicia tanto el socket como el hilo de recepción."""
        self.iniciar_rpc()
        self.iniciar_socket()
        self.running = True
        hilo = threading.Thread(target=self.recibir_evento, daemon=True)
        hilo.start()

    def detener(self):
        """Cierra las conexiones."""
        self.running = False
        if hasattr(self, "conn"):
            self.conn.close()
        if self.sock:
            self.sock.close()
        if self.rpc_proxy:
            self.rpc_proxy._pyroRelease()



#Ejemplo de uso
if __name__ == "__main__":

# test_servidor.py
    if __name__ == "__main__":
        dir_socket = ("localhost", 5000)
        dir_rpc = "PYRO:servidor@localhost:9090"
        conexion = ConexionServidor(dir_rpc, dir_socket)

        print("Servidor escuchando en", dir_socket)
        while True:
            pass  # mantener el main vivo


#test_cliente.py
if __name__ == "__main__":
    dir_socket = ("localhost", 5000)
    dir_rpc = "PYRO:servidor@localhost:9090"

    conexion = ConexionCliente(dir_rpc, dir_socket)

    #Esta conexion utiliza ambos manejadores. 
    #El servidor tiene otro tipo de conexion con sus metodos de recepcion y broadcasting
    #La replica seria otro tipo de cliente, pero con su propia conexion ConexionReplica.py


    print("Cliente conectado al servidor.")

    # probar enviar un heartbeat
    conexion.enviar_heartbeat()

    # mantener proceso vivo un rato para recibir respuesta
    import time
    time.sleep(2)
