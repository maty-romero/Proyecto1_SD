import Pyro5.nameserver
import socket
import threading
import time
from GestorPartida import GestorPartida
from test_flujo_juego.ComunicationHelper import ComunicationHelper

def obtener_ip_local():
    """Obtiene la IP local de forma dinámica."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def iniciar_servidor_nombres(host_ip: str):
    """Función que se ejecutará en un hilo para iniciar el NS."""
    print(f"[Servidor de Nombres] Iniciando en {host_ip}...")
    Pyro5.nameserver.start_ns_loop(host=host_ip)
    print("[Servidor de Nombres] Detenido.")


if __name__ == "__main__":
    ip_servidor = ComunicationHelper.obtener_ip_local()
    ComunicationHelper.iniciar_servidor_nombres_en_hilo(ip_servidor)

    daemon = Pyro5.api.Daemon(host=ip_servidor)
    ns = Pyro5.api.locate_ns()

    objeto_registro_singleton = GestorPartida()
    nombre_logico = "gestor.partida"

    uri = ComunicationHelper.registrar_objeto_en_ns(
        objeto_registro_singleton,
        nombre_logico,
        daemon,
        ns)

    print(f"[Servidor Lógico] Listo y escuchando en {ip_servidor}")
    daemon.requestLoop()