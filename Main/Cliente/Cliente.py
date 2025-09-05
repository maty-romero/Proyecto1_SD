import threading
import time

import Pyro5.api
import sys

from ServicioCliente import ClienteJugadorService
from Main.Utils.ComunicationHelper import ComunicationHelper
from Main.Common.AbstractGUI import AbstractGUI
from Main.Common.ConsoleGUI import ConsoleGUI

class ClienteHelper:
    def __init__(self, gui: AbstractGUI):
        self.gui = gui
    
    def solicitar_nickname_valido(self, proxy_partida) -> str:
        """Solicita al usuario un nickname único y válido para la partida."""
        nickname = self.gui.get_input("Para jugar, ingrese su NickName para la partida: ")
        formated_nickname = nickname.lower().replace(" ", "")
        is_unique = proxy_partida.CheckNickNameIsUnique(formated_nickname)

        if not isinstance(is_unique, bool):
            self.gui.show_message("Debe ingresar un STRING válido. Ejecute nuevamente el script Cliente.")
            sys.exit(1)

        while not is_unique:
            nickname = self.gui.get_input("\nEl NickName ingresado ya está siendo utilizado. Ingrese otro: ")
            formated_nickname = nickname.lower().replace(" ", "")
            is_unique = proxy_partida.CheckNickNameIsUnique(formated_nickname)
        return formated_nickname

    def mostrar_mensaje(self, mensaje: str):
        self.gui.show_message(mensaje)

def main():
    nombre_logico_partida = "gestor.partida"
    try:
        proxy_partida = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico_partida}")

    except Pyro5.errors.NamingError:
        print(f"Error: No se pudo encontrar el objeto '{nombre_logico_partida}'.")
        print("Asegúrese de que el Servidor de Nombres y el servidor.py estén en ejecución.")
        sys.exit(1)

    print("Conectado al servidor de registro.")

    auxClient = ClienteHelper(ConsoleGUI())

    # Check if NickName is Unique
    nickname = auxClient.solicitar_nickname_valido(proxy_partida)
    auxClient.mostrar_mensaje(f"NickName confirmado: {nickname}")

    # Registrar objeto remoto del cliente en Servidor

    ip_cliente = ComunicationHelper.obtener_ip_local()
    objeto_cliente = ClienteJugadorService(ConsoleGUI()) # Crear objeto remoto del cliente
    nombre_logico_jugador = f"jugador.{nickname}"

    def daemon_loop(): # Crear Daemon y registrar objeto en NS usando CommunicationHelper
        daemon = Pyro5.server.Daemon(host=ip_cliente)
        #ns = Pyro5.api.locate_ns()
        # Uso de NickName para registro del objeto
        uri = ComunicationHelper.registrar_objeto_en_ns(objeto_cliente, nombre_logico_jugador, daemon)
        auxClient.mostrar_mensaje(f"[Registro] Objeto CLIENTE '{nickname}' disponible en URI: {uri}")
        daemon.requestLoop()

    hilo_daemon = threading.Thread(target=daemon_loop)
    hilo_daemon.daemon = True
    hilo_daemon.start()

    time.sleep(3)  # Espera para que el hilo imprima el URI

    print(f"✅ Cliente '{nickname}' listo para Unirse a la sala!.")
    print(f"✅ NombreLogico: '{nombre_logico_jugador}' para objeto rem")
    print(f"✅ Proxy_Partida: '{proxy_partida}'")
    # Cliente se Une a la sala 
    proxy_partida.unirse_a_sala(nickname, nombre_logico_jugador) # ejecuta envio_info_sala desde server
    # (Recibe info en consola cliente)

# ---------------------------------------- Acá se empieza a jugar

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