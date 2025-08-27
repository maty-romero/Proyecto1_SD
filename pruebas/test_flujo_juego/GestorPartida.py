from Partida import Partida
import Pyro5.api

@Pyro5.api.expose
class GestorPartida:
    def __init__(self):
        self.partida = Partida() # jugadores, categorias y nro ronda
        print("[Servidor Lógico] Objeto Gestor Partida Inicializado.")

    def test_ejecucion_obj_cliente(self, nickname: str, mensaje: str):
        print("*** Server envia mennsaje a Cliente ***")
        jugador_remoto = self.partida.get_jugador(nickname)
        jugador_remoto.recibir_info_sala(mensaje)


    def registrar_nodo_cliente(self, nickname: str, nombre_logico: str):
        proxy_cliente = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico}")
        print(f"Registrando jugador: {nickname}, con nombre_logico: {nombre_logico}")

        # se agrega objeto remoto
        self.partida.agregar_jugador_partida(nickname, proxy_cliente)

        # devolver json info para la sala
        info_partida_json = self.partida.get_info_partida_json();

        # prueba - borrar consola cliente e imprimir json info sala
        self.test_ejecucion_obj_cliente(nickname, info_partida_json)
        #return info_partida_json

    def CheckNickNameIsUnique(self, nickname: str):
        is_not_string = not isinstance(nickname, str)
        if (nickname == "" or is_not_string):
            return "Error: NickName vacio o no es cadena!"

        formated_nickname = nickname.lower().strip(' ');
        is_unique: bool = self.partida.is_nickname_disponible(formated_nickname)
        return is_unique
