import sys
import time
import traceback
import Pyro5.server

from Cliente.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.NodoReplica import NodoReplica
from Servidor.Utils.ComunicationHelper import ComunicationHelper
from Servidor.Utils.ConsoleLogger import ConsoleLogger
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf

"""-Futura implementacion: Para manipular ids, podemos hacer que se registre una lista de nodos en el NS,
    o alguna otra similar para poder incrementar esa id y que cada nodo se identifique de manera unica,
    por ejemplo que al momento del registro el nodo incremente un contador en el nameserver,
    pero si se cae, esto puede que no sea tan util.
    """

def medir_tiempo (t1,t2):
    return t2-t1

class ReplicaListener:
    def remove_service(self, zeroconf, type, name):
        pass
    def add_service(self, zeroconf, type, name):
        servicios_encontrados.append(name)


if __name__ == "__main__":
    ip_local=ComunicationHelper.obtener_ip_local()
    puerto_local_replica=5000
    logger = ConsoleLogger(name="mainServer", level="INFO")

#-----------------------------------Buscar otras terminales-----------------------------------#

    from zeroconf import Zeroconf, ServiceBrowser, ServiceInfo
    import socket
    import time

    zeroconf = Zeroconf()
    servicios_encontrados = []

    
    # tipo de servicio que registran tus réplicas, por ej "_replica._tcp.local."
    tipo_servicio = "_replica._tcp.local."
    browser = ServiceBrowser(zeroconf, tipo_servicio, ReplicaListener())

    # Esperar un par de segundos para que se descubran los servicios
    time.sleep(2)

    # Contar cuántas réplicas hay para asignar ID
    nro_nodo = len(servicios_encontrados) + 1

    # Datos de la réplica local
    ip_local = socket.gethostbyname(socket.gethostname())
    puerto_local_replica = 5000  # ejemplo

    Replica_Local = NodoReplica(
        nro_nodo,
        ip_local,
        puerto_local_replica,
        "Replica",
        False
    )

    Replicas_Vecinas = servicios_encontrados.copy()

    # Esperar hasta que haya al menos 3 réplicas vecinas
    while len(Replicas_Vecinas) < 3:
        print("Faltan replicas para iniciar...")
        servicios_encontrados.clear()
        time.sleep(1)

        # Recargar la lista de servicios en cache
        for entry in zeroconf.cache.entries():
            if entry.type == tipo_servicio:
                servicios_encontrados.append(entry.name)

        Replicas_Vecinas = servicios_encontrados.copy()

    print("Se encontraron todas las replicas, iniciando...")

    #metodo para inicializar replica




#-----------------------------------Buscar y conectar a servidor de nombres-----------------------------------#
 


#------------------------------------Inicio de Conexion Replicas--------------------------------------#
    # try:



    #     ip_local = ComunicationHelper.obtener_ip_local()

    #     # id mas grande por Bully
    #     nodoPrincipal = NodoReplica(id=30, host=ip_localhost, puerto=5000, nombre="NodoPpal", esCoordinador=True)
    #     # activo = false por defecto

    #     # Todos los nodos deben conocerse entre si - condicion de algoritmo Bully
    #     # Refactorizar lo siguiente ??
    #     nodoPrincipal.registrar_nodo_en_cluster(nodoReplica1)
    #     nodoReplica1.conectarse_a_coordinador()


    #     Gestor_Singleton = nodoPrincipal.ServicioJuego
    #     #daemon = Pyro5.server.Daemon(host=ip_servidor)
    #     daemon = Pyro5.server.Daemon(host=ip_localhost)

    #     uri = ComunicationHelper.registrar_objeto_en_ns(
    #         Gestor_Singleton,
    #         "gestor.partida",
    #         daemon
    #     )

    #     logger.info("ServicioJuego registrado correctamente.")
    #     logger.debug(f"URI: {uri}")
    #     logger.debug(f"Daemon: {daemon}")
    #     daemon.requestLoop()

    # except Exception as e:
    #     print(f"Error inesperado: {e}")
    #     traceback.print_exc()  # esto imprime la traza completa
