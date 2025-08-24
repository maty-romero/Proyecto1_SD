import Pyro5.nameserver
import socket
import threading
import time
from RegistroClientesPartida import RegistroClientesPartida
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


def iniciar_servidor_nombres(host_ip):
    """Función que se ejecutará en un hilo para iniciar el NS."""
    print(f"[Servidor de Nombres] Iniciando en {host_ip}...")
    Pyro5.nameserver.start_ns_loop(host=host_ip)
    print("[Servidor de Nombres] Detenido.")


if __name__ == "__main__":
    ip_servidor = obtener_ip_local()

    ns_thread = threading.Thread(target=iniciar_servidor_nombres, args=(ip_servidor,))
    ns_thread.daemon = True  # El hilo del NS terminará cuando el programa principal lo haga.
    ns_thread.start()

    time.sleep(1)  # tiempo para que el NS inicie

    daemon = Pyro5.api.Daemon(host=ip_servidor)
    ns = Pyro5.api.locate_ns()
    # Descomentar la linea de abajo si se quiere un nuevo objeto por cliente
    # uri = daemon.register(RegistroNodos, objectId="registro_nodos")
    # La dos lineas de abajo disponibilizan un singleton para que todos los clientes compartan el mismo objeto
    objeto_registro_singleton = RegistroClientesPartida()
    uri = daemon.register(objeto_registro_singleton, objectId="registro_clientes_partida")
    nombre_logico = "registro.clientes"
    ns.register(nombre_logico, uri)

    print(f"[Servidor Lógico] Listo y escuchando en {ip_servidor}")
    print(f"URI del objeto: {uri}")

    daemon.requestLoop()
    # este codigo crea un servidor de nombres y un servidor lógico que registra nodos conectados
    # y permite a los clientes obtener la lista de nodos registrados.