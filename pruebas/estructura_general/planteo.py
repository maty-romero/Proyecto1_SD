# conexion/publisher.py
class PublisherRPCSocket implements INotificador
    def __init__(self, rpc_handler, socket_handler):
        self._rpc    = rpc_handler
        self._socket = socket_handler

    def register_player(self, jugador_id, proxy_or_ws):
        """
        Se llama desde GestorPartida.agregar_jugador() o 
        directamente desde ManejadorRPC en el hook join_jugador.
        """
        self._rpc.proxies[jugador_id]   = proxy_or_ws  # si es PyroProxy
        # o si es WS: self._socket.clients[jugador_id] = proxy_or_ws

    # mas general --> 2 metodos: broadcast y unicast 
    # o varios metodos y dependiendo la notificacion usar a traves de manejadores, socket o pyro
    def unregister_player(self, jugador_id):
        self._rpc.proxies.pop(jugador_id, None)
        self._socket.clients.pop(jugador_id, None)

    def broadcast(self, mensaje: dict):
        for proxy in self._rpc.proxies.values():
            proxy.recibir_evento(mensaje)
        for ws in self._socket.clients.values():
            ws.send_json(mensaje)

    def unicast(self, jugador_id: str, mensaje: dict):
        if jugador_id in self._rpc.proxies:
            self._rpc.proxies[jugador_id].recibir_evento(mensaje)
        if jugador_id in self._socket.clients:
            self._socket.clients[jugador_id].send_json(mensaje)

class NodoServidor():
    def __init__(self, min_jugadores):
        super().__init__()
        # Creamos la capa de red
        self.conexion = ConexionServidor()
        # Inyectamos el publisher en el gestor
        self.gestor   = GestorPartida(publisher=self.conexion.publisher,
                                      min_jugadores=min_jugadores)
    

class ConexionServidor implements IServicioRemoto:
    def __init__(self):
        self.rpc    = ManejadorRPC()      # expone objetos Pyro
        self.socket = ManejadorSocket()   # expone WebSockets, heartbeats…
        # El publisher es quien registra jugadores y notifica mensajes
        self.publisher = PublisherRPCSocket(self.rpc, self.socket)

    def registrar_servicio(self, gestor):
        # Registramos solo métodos de negocio que GestorPartida expone
        self.rpc.registrar_servicio(gestor)
        # Si fuese necesario, también podríamos registrar hooks en el socket

    def Iniciar_servicios(self):
        # Arrancar RPC y Sockets en hilos distintos
        self.rpc.serve_forever()
        self.socket.serve_forever()

    def Detener_Servicios(self):
        self.rpc.shutdown()
        self.socket.shutdown()


class GestorPartida():
    def __init__(self, INotificador, IServicioRemoto):
        self.notificador = INotificador # Socket y Pyro hacia clientes 
        self.servicio_remoto = IServicioRemoto # metodos de RPC 

    # metodos expuestos que puede usar el cliente en GestorCliente

interface IServicioRemoto: 
    - unirse_a_sala()
    - buscar_jugador
    - 
