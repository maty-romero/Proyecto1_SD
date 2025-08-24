from Partida import Partida
import Pyro5.api

@Pyro5.api.expose
class RegistroClientesPartida:
    def __init__(self):
        self.partida = Partida() # jugadores, categorias y nro ronda
        print("[Servidor Lógico] Objeto de registro inicializado.")

    def registrar_nodo_cliente(self, nickname: str):
        ip_cliente = Pyro5.api.current_context.client_sock_addr[0] # ip cliente que manda request
        print(f"[Servidor Lógico] Registrando nodo desde: {ip_cliente}")
        self.partida.agregar_jugador_partida(ip_cliente, nickname)

        info_partida_json = self.partida.get_info_partida_json();
        return info_partida_json

    """
    def obtener_nodos_registrados(self):
        print("[Servidor Lógico] Petición de lista de nodos recibida.")
        return list(self.nodos_conectados)
    """