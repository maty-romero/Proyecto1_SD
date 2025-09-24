import Pyro5.server
from Pyro5 import errors
from Pyro5.errors import NamingError, CommunicationError

from Servidor.Utils.ComunicationHelper import ComunicationHelper
from Servidor.Aplicacion.NodoServidor import NodoServidor
from Servidor.Utils.ConsoleLogger import ConsoleLogger

"""-Futura implementacion: Para manipular ids, podemos hacer que se registre una lista de nodos en el NS,
    o alguna otra similar para poder incrementar esa id y que cada nodo se identifique de manera unica,
    por ejemplo que al momento del registro el nodo incremente un contador en el nameserver,
    pero si se cae, esto puede que no sea tan util.
    """
if __name__ == "__main__":
    logger = ConsoleLogger(name="mainServer", level="INFO")
    logger.info("Iniciando servidor principal...")

    try:
        ns = Pyro5.api.locate_ns()
        logger.info("Servidor de nombres localizado correctamente.")
    except (NamingError, CommunicationError, ConnectionRefusedError) as e:
        logger.error(f"No se pudo conectar al servidor de nombres: {e}")
        logger.warning("Abortando inicio del servidor.")
        exit(1)

    try:
        ip_servidor = ComunicationHelper.obtener_ip_local()
        nodoPrincipal = NodoServidor(1, True)
        Gestor_Singleton = nodoPrincipal.ServicioJuego
        daemon = Pyro5.server.Daemon(host=ip_servidor)

        uri = ComunicationHelper.registrar_objeto_en_ns(
            Gestor_Singleton,
            "gestor.partida",
            daemon,
            ns
        )

        logger.info("Gestor de juego registrado correctamente.")
        logger.debug(f"URI: {uri}")
        logger.debug(f"Daemon: {daemon}")
        daemon.requestLoop()

    except NamingError:
        logger.error("Servidor de nombres no encontrado.")
    except CommunicationError:
        logger.error("Error de comunicación con el Servidor de nombres.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")