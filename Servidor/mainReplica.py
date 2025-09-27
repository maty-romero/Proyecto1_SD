import sys
import time
import traceback
import Pyro5.server

from Cliente.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.NodoReplica import NodoReplica
from Servidor.Utils.ComunicationHelper import ComunicationHelper
from Servidor.Utils.ConsoleLogger import ConsoleLogger

"""-Futura implementacion: Para manipular ids, podemos hacer que se registre una lista de nodos en el NS,
    o alguna otra similar para poder incrementar esa id y que cada nodo se identifique de manera unica,
    por ejemplo que al momento del registro el nodo incremente un contador en el nameserver,
    pero si se cae, esto puede que no sea tan util.
    """

def medir_tiempo (t1,t2):
    return t2-t1

if __name__ == "__main__":
    ip_local=ComunicationHelper.obtener_ip_local()
    puerto_local_replica=5000
    logger = ConsoleLogger(name="mainServer", level="INFO")

#-----------------------------------Buscar otras terminales-----------------------------------#

    #obtener registros dns
    nro_nodo = None+1 #count(zeroconf.nombres)
    Replica_Local = NodoReplica(nro_nodo,
        ip_local,
        puerto_local_replica,
        "Replica",
        False)

    Replicas_Vecinas=[]









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
