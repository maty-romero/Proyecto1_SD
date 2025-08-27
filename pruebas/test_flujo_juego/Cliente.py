import threading
import time

import Pyro5.api
import sys

from test_flujo_juego.ClienteJugador import ClienteJugador
from test_flujo_juego.ComunicationHelper import ComunicationHelper


def solicitar_nickname_valido(proxy_partida) -> str:
    """Solicita al usuario un nickname único y válido para la partida."""
    nickname = input("Para jugar, ingrese su NickName para la partida: ")
    is_unique = proxy_partida.CheckNickNameIsUnique(nickname)

    if not isinstance(is_unique, bool):
        print("Debe ingresar un STRING válido. Ejecute nuevamente el script Cliente.")
        sys.exit(1)

    while not is_unique:
        nickname = input("\nEl NickName ingresado ya está siendo utilizado. Ingrese otro: ")
        is_unique = proxy_partida.CheckNickNameIsUnique(nickname)

    return nickname


def main():
    nombre_logico = "gestor.partida"
    try:
        proxy_partida = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico}")

    except Pyro5.errors.NamingError:
        print(f"Error: No se pudo encontrar el objeto '{nombre_logico}'.")
        print("Asegúrese de que el Servidor de Nombres y el servidor.py estén en ejecución.")
        sys.exit(1)

    print("Conectado al servidor de registro.")

    # Check if NickName is Unique
    nickname = solicitar_nickname_valido(proxy_partida)
    print(f"NickName confirmado: {nickname}")

    # Registrar objeto remoto del cliente en Servidor

    ip_cliente = ComunicationHelper.obtener_ip_local()
    objeto_cliente = ClienteJugador(nickname) # Crear objeto remoto del cliente

    def daemon_loop(): # Crear Daemon y registrar objeto en NS usando CommunicationHelper
        daemon = Pyro5.server.Daemon(host=ip_cliente)
        ns = Pyro5.api.locate_ns()
        # Uso de NickName para registro del objeto
        uri = ComunicationHelper.registrar_objeto_en_ns(objeto_cliente, f"jugador.{nickname}", daemon, ns)
        print(f"[Registro] Objeto CLIENTE '{nickname}' disponible en URI: {uri}")
        daemon.requestLoop()

    hilo_daemon = threading.Thread(target=daemon_loop)
    hilo_daemon.daemon = True
    hilo_daemon.start()

    time.sleep(3)  # Espera para que el hilo imprima el URI

    print(f"✅ Cliente '{nickname}' listo para registrar!.")
    # metodo remoto: GestorPartida.registrar_nodo_cliente(self, nickname: str, nombre_logico: str):
    proxy_partida.registrar_nodo_cliente(nickname, f"jugador.{nickname}") # registro para broadcasting


if __name__ == "__main__":
    main()