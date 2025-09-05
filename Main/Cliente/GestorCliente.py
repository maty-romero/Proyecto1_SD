import sys
import threading
import time
import Pyro5

from Main.Cliente.JugadorCliente import JugadorCliente
from Main.Common.AbstractGUI import AbstractGUI
from Main.Common.ConsoleGUI import ConsoleGUI
from Main.Utils.ComunicationHelper import ComunicationHelper
from Main.Cliente.ServicioCliente import ServicioCliente

class GestorCliente:
    def __init__(self, gui: AbstractGUI):
        self.gui = gui
        self.nombre_logico_server = "gestor.partida"
        self.proxy_partida = None # inicializa en get_proxy_partia_singleton
        self.jugador_cliente = None # inicializa en ingresar_nickname_valido


    def get_proxy_partida_singleton(self):
        if self.proxy_partida is None:
            try:
                self.proxy_partida = Pyro5.api.Proxy(f"PYRONAME:{self.nombre_logico_server}")
            except Pyro5.errors.NamingError:
                self.gui.show_error(f"Error: No se pudo encontrar el objeto '{self.nombre_logico_server}'.")
                self.gui.show_message(
                    "Asegúrese de que el Servidor de Nombres y el servidor.py estén en ejecución.")
                sys.exit(1)

        return self.proxy_partida  # ya existe una instancia

    def buscar_partida(self):
        # simulacion de buscar partida, verificacion de que hay un servidor de nombres??
        pass

    def ingresar_nickname_valido(self) -> bool:
        nickname = self.gui.get_input("Para jugar, ingrese su NickName para la partida: ")
        formated_nickname = nickname.lower().replace(" ", "")
        is_unique = self.get_proxy_partida_singleton().CheckNickNameIsUnique(formated_nickname)

        while not is_unique:
            nickname = self.gui.get_input("\nEl NickName ingresado ya está siendo utilizado. Ingrese otro: ")
            formated_nickname = nickname.lower().replace(" ", "")
            is_unique = self.get_proxy_partida_singleton().CheckNickNameIsUnique(formated_nickname)

        self.gui.show_message(f"NickName '{nickname}' confirmado!")
        self.jugador_cliente = JugadorCliente(nickname)

        self.inicializar_Deamon_Cliente(
            self.jugador_cliente.get_nickname(),
            self.jugador_cliente.get_nombre_logico()
        )


    def inicializar_Deamon_Cliente(self, nickname: str, nombre_logico_jugador: str):
        ip_cliente = ComunicationHelper.obtener_ip_local()
        objeto_cliente = ServicioCliente(ConsoleGUI())  # Crear objeto remoto del cliente
        nombre_logico_jugador = f"jugador.{nickname}"

        def daemon_loop():  # Crear Daemon y registrar objeto en NS usando CommunicationHelper
            daemon = Pyro5.server.Daemon(host=ip_cliente)
            # ns = Pyro5.api.locate_ns()
            # Uso de NickName para registro del objeto
            uri = ComunicationHelper.registrar_objeto_en_ns(objeto_cliente, nombre_logico_jugador, daemon)
            self.gui.show_message(f"[Registro] Objeto CLIENTE '{nickname}' disponible en URI: {uri}")
            daemon.requestLoop()

        hilo_daemon = threading.Thread(target=daemon_loop)
        hilo_daemon.daemon = True
        hilo_daemon.start()

        time.sleep(2)  # Espera para que el hilo imprima el URI

    def unirse_a_sala(self):
        self.gui.show_message(f"Jugador '{self.jugador_cliente.get_nickname}' uniendose a la sala...")

        self.get_proxy_partida_singleton().unirse_a_sala(
            self.jugador_cliente.get_nickname(),
            self.jugador_cliente.get_nombre_logico
        )
        self.gui.show_message(f"Jugador '{self.jugador_cliente.get_nickname}' se ha unido a la sala!")

    def confirmar_jugador_partida(self):
        self.gui.show_message(f"Confirmando jugador: '{self.jugador_cliente.get_nickname}'")
        self.get_proxy_partida_singleton().confirmar_jugador(self.jugador_cliente.get_nickname())
        self.gui.show_message(f"Jugador: '{self.jugador_cliente.get_nickname}' Confirmado. Espere a que inicie la ronda.")

    def jugar_nueva_ronda(self):
        # instanciar objeto de RondaCliente
        # al final obtener diccionario para mandar a servidor -> uso de RondaCliente.getRespuestasJugador
        pass

    """ 
    def get_jugador_cliente(self):
        if self.jugador_cliente is None:
            self.gui.show_message("Debe iniciar sesion ingresando un nickname!")
            return None
        return self.jugador_cliente
    """

"""
def main():

    # Simulacion de cliente jugando --> prueba
    respuesta = proxy_partida.confirmar_jugador()
    print("Respuesta del servidor:", respuesta)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Cliente cerrado manualmente.")

    # info_ronda_json = proxy_partida.confirmar_jugador() # simulacion de confirmacion
    # print(f"INFO RONDA EN CLIENTE PARA JUGAR (JSON) {info_ronda_json}")

    # infoRonda = json.loads(info_ronda_json, object_hook=lambda d: SimpleNamespace(**d))
    # print(f"Cliente Jugando Ronda: {infoRonda.nro_ronda}")
    # infoRonda.letra_ronda = 'A'
    # print(f"Letra Ronda: {infoRonda.letra_ronda}. Comienza la ronda!")

    # respuestasDict = {clave: "" for clave in infoRonda.categorias}

    # for clave in respuestasDict:
    #     respuesta = input(f"Ingrese respuesta para categoria[{clave}]: ")
    #     # Validacion primer letra 
    #     while respuesta.upper()[0] != infoRonda.letra_ronda:
    #         print(f"Estamos jugando con la letra {infoRonda.letra_ronda}!")
    #         respuesta = input(f"Ingrese respuesta para categoria [{clave}]: ")

    #     respuestasDict[clave] = respuesta

    # json_respuestas = json.dumps(respuestasDict) # JSON
    # print(f"La respuestas del cliente son: {json_respuestas}")
    # print("\nPENDIENTE - Enviar respuestas a nodo server")


if __name__ == "__main__":
    main()

"""