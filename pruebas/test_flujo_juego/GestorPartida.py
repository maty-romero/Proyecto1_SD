from Partida import Partida
import Pyro5.api

@Pyro5.api.expose
class GestorPartida:
    def __init__(self):
        self.partida = Partida() # jugadores, categorias y nro ronda
        print("[Servidor Lógico] Objeto Gestor Partida Inicializado.")

    def registrar_nodo_cliente(self, nickname: str):
        ip_cliente = Pyro5.api.current_context.client_sock_addr[0] # ip cliente que manda request
        print(f"[Servidor Lógico] Registrando nodo desde: {ip_cliente}")
        # Obtener Uri Cliente etc.
        self.partida.agregar_jugador_partida(ip_cliente, nickname)

        info_partida_json = self.partida.get_info_partida_json();
        return info_partida_json

    def CheckNickNameIsUnique(self, nickname: str):
        is_not_string = not isinstance(nickname, str)
        if (nickname == "" or is_not_string):
            return "Error: NickName vacio o no es cadena!"

        formated_nickname = nickname.lower().strip(' ');
        is_unique: bool = self.partida.is_nickname_disponible(formated_nickname)
        return is_unique
