import traceback
import Pyro5.server
from Pyro5 import errors
from Pyro5.errors import NamingError, CommunicationError

from Servidor.Aplicacion.NodoReplica import NodoReplica
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
    """ """
    try:
        ns = Pyro5.api.locate_ns()
        logger.info("Servidor de nombres localizado correctamente.")
    except (NamingError, CommunicationError, ConnectionRefusedError) as e:
        logger.error(f"No se pudo conectar al servidor de nombres: {e}")
        logger.warning("Abortando inicio del servidor.")
        exit(1)

    try:
        #ip_servidor = ComunicationHelper.obtener_ip_local()
        ip_localhost = "127.0.0.1"

        # id mas grande por Bully
        nodoPrincipal = NodoServidor(id=30, host=ip_localhost, puerto=5000, nombre="NodoPpal", activo=True)
        # activo = false por defecto
        #id, host, puerto, coordinador_id: int, nombre="Replica", activo=False
        nodoReplica1 = NodoReplica(id=15, host=ip_localhost, puerto=5001,
                                   coordinador_id=nodoPrincipal.id, nombre="Replica1", )
        nodoReplica2 = NodoReplica(id=10, host=ip_localhost, puerto=5002,
                                   coordinador_id=nodoPrincipal.id, nombre="Replica2")

        # Todos los nodos deben conocerse entre si - condicion de algoritmo Bully
        # Refactorizar lo siguiente ??
        nodoPrincipal.registrar_nodo_en_cluster(nodoReplica1)
        nodoPrincipal.registrar_nodo_en_cluster(nodoReplica2)

        nodoReplica1.registrar_nodo_en_cluster(nodoPrincipal)
        nodoReplica1.registrar_nodo_en_cluster(nodoReplica2)

        nodoReplica2.registrar_nodo_en_cluster(nodoPrincipal)
        nodoReplica2.registrar_nodo_en_cluster(nodoReplica1)

        nodoPrincipal.iniciar_servicio()
        nodoReplica1.iniciar_replica()
        nodoReplica2.iniciar_replica()

        Gestor_Singleton = nodoPrincipal.ServicioJuego
        #daemon = Pyro5.server.Daemon(host=ip_servidor)
        daemon = Pyro5.server.Daemon(host=ip_localhost)

        uri = ComunicationHelper.registrar_objeto_en_ns(
            Gestor_Singleton,
            "gestor.partida",
            daemon
        )

        logger.info("ServicioJuego registrado correctamente.")
        logger.debug(f"URI: {uri}")
        logger.debug(f"Daemon: {daemon}")
        daemon.requestLoop()

#    except errors.NamingError:
#        print("Servidor de nombres no encontrado")
#    except errors.CommunicationError:
#        print("Error de comunicación con el Servidor de nombres")
    except Exception as e:
        print(f"Error inesperado: {e}")
        traceback.print_exc()  # esto imprime la traza completa
    #else: 
#        print("No se puede ejecutar el Servidor, dado que el Servidor de nombres no se esta ejecutando. ")
