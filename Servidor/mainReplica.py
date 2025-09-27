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

import socket
import time
from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser
from Servidor.Aplicacion.NodoReplica import NodoReplica
from Servidor.Utils.ConsoleLogger import ConsoleLogger

logger = ConsoleLogger("MainReplica", "INFO")

# ---------- Configuración ----------
tipo_servicio = "_replica._tcp.local."
ip_local = socket.gethostbyname(socket.gethostname())
puerto_local_replica = 5001  # puerto de la réplica local
max_replicas = 3

zeroconf = Zeroconf()

# ---------- Listener para descubrir réplicas ----------
class ReplicaListener:
    def __init__(self):
        self.replicas_detectadas = {}

    def add_service(self, zeroconf, tipo, name):
        info = zeroconf.get_service_info(tipo, name)
        if info:
            rid = int(info.properties[b"replica-id"])
            self.replicas_detectadas[rid] = {
                "name": name,
                "ip": socket.inet_ntoa(info.addresses[0]),
                "port": info.port
            }
            logger.info(f"Se detectó réplica: {name} (ID {rid})")

    # Método requerido por Zeroconf (puede estar vacío)
    def update_service(self, zeroconf, tipo, name):
        pass

    def remove_service(self, zeroconf, tipo, name):
        # Podés manejar desconexiones si querés
        pass

listener = ReplicaListener()
browser = ServiceBrowser(zeroconf, tipo_servicio, listener)

# ---------- Esperar un momento para detectar réplicas existentes ----------
time.sleep(1.5)

# ---------- Calcular ID único ----------
ids_existentes = list(listener.replicas_detectadas.keys())
nro_nodo = max(ids_existentes, default=0) + 1

# ---------- Registrar réplica local ----------
info_local = ServiceInfo(
    type_=tipo_servicio,
    name=f"replica-{nro_nodo}._replica._tcp.local.",
    addresses=[socket.inet_aton(ip_local)],
    port=puerto_local_replica,
    properties={
        "replica-id": str(nro_nodo),
        "ip": ip_local,
        "puerto": str(puerto_local_replica)
    },
    server=f"replica-{nro_nodo}.local."
)

zeroconf.register_service(info_local, allow_name_change=True)
logger.info(f"Réplica local registrada con ID {nro_nodo}")

# ---------- Crear instancia de NodoReplica ----------
Replica_Local = NodoReplica(nro_nodo, ip_local, puerto_local_replica, "Replica", False)

# ---------- Esperar a que se encuentren las réplicas vecinas ----------
Replicas_Vecinas = []
timeout = 15  # segundos
inicio = time.time()

while len(Replicas_Vecinas) < max_replicas:
    Replicas_Vecinas = list(listener.replicas_detectadas.values())
    if len(Replicas_Vecinas) < max_replicas:
        logger.warning(f"Faltan replicas para iniciar. Detectadas: {len(Replicas_Vecinas)}")
        time.sleep(1)
    if time.time() - inicio > timeout:
        logger.warning("Timeout alcanzado, continuando con las réplicas encontradas")
        break

logger.info(f"Réplicas detectadas: {Replicas_Vecinas}")
logger.info("Iniciando NodoReplica local...")

# ---------- Aquí podés iniciar la lógica de NodoReplica ----------
# Replica_Local.iniciar_como_coordinador(...) o conectarse a un coordinador existente

# ---------- Mantener la aplicación corriendo ----------
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Finalizando...")
finally:
    zeroconf.unregister_service(info_local)
    zeroconf.close()

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
