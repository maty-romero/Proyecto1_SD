
import socket
import Pyro5
from Servidor.Aplicacion.NodoReplica import NodoReplica
from Utils.ConsoleLogger import ConsoleLogger
from Pyro5.errors import NamingError, CommunicationError

if __name__ == "__main__":

    logger = ConsoleLogger(name="mainServer", level="INFO")
    logger.info("Iniciando servidor principal...")
    """ """
    try:
        ns = Pyro5.api.locate_ns()
        logger.info("Servidor de nombres localizado correctamente.")
    except (NameError, CommunicationError, ConnectionRefusedError) as e:
        logger.error(f"No se pudo conectar al servidor de nombres: {e}")
        logger.warning("Abortando inicio del servidor.")
        exit(1)

    #ip_servidor = ComunicationHelper.obtener_ip_local()
    ip_local = socket.gethostbyname(socket.gethostname())
    puerto_local = 5000
    nro_nodo = 1

    Replica_Local = NodoReplica(nro_nodo, ip_local, puerto_local, "Replica", False)

    #se registra como un nodo en su lista
    #NO SE TIENE QUE REGISTRAR A SI MISMA
    #Replica_Local.registrar_nodo(Replica_Local.id,Replica_Local.nombre,ip_local,puerto_local)
    logger.warning(f"Replica creada con datos:{nro_nodo, ip_local, puerto_local, 'Replica'}")
        # ---------- Mantener activo ----------
    logger.info("Iniciando booly de replica")
    Replica_Local.iniciar_eleccion()