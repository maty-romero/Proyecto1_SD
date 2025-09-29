import sys
import time
import traceback
import Pyro5.server

from Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.NodoReplica import NodoReplica
from Utils.ComunicationHelper import ComunicationHelper
from Utils.ConsoleLogger import ConsoleLogger
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
import socket
import time
from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser
from Servidor.Aplicacion.NodoReplica import NodoReplica
from Utils.ConsoleLogger import ConsoleLogger

"""-Futura implementacion: Para manipular ids, podemos hacer que se registre una lista de nodos en el NS,
    o alguna otra similar para poder incrementar esa id y que cada nodo se identifique de manera unica,
    por ejemplo que al momento del registro el nodo incremente un contador en el nameserver,
    pero si se cae, esto puede que no sea tan util.
    """

def medir_tiempo (t1,t2):
    return t2-t1

def obtener_puerto_libre():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))  # el sistema asigna un puerto libre
        _, puerto = s.getsockname()
        s.close()
        return puerto


import socket
import time
import random
from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser

def obtener_id_unico_con_retry(zeroconf, tipo_servicio, ip_local, puerto_local, max_intentos=5):
    """
    Solución simple: retry con backoff exponencial y jitter aleatorio
    """
    base_delay = 0.1
    
    for intento in range(max_intentos):
        try:
            # Jitter aleatorio para evitar sincronización
            if intento > 0:
                jitter = random.uniform(0, 0.1)
                delay = (base_delay * (2 ** (intento - 1))) + jitter
                print(f"Intento {intento + 1}, esperando {delay:.3f}s...")
                time.sleep(delay)
            
            # Descubrir réplicas existentes
            class TempListener:
                def __init__(self):
                    self.replicas = {}
                def add_service(self, zc, tipo, name):
                    info = zc.get_service_info(tipo, name)
                    if info and b"replica-id" in info.properties:
                        rid = int(info.properties[b"replica-id"])
                        self.replicas[rid] = True
                def update_service(self, *args): pass
                def remove_service(self, *args): pass
            
            temp_listener = TempListener()
            ServiceBrowser(zeroconf, tipo_servicio, temp_listener)
            time.sleep(1.2)  # Tiempo para descubrimiento
            
            # Calcular nuevo ID
            nro_nodo = max(temp_listener.replicas.keys(), default=0) + 1
            nombre_replica = f"replica-{nro_nodo}"
            
            print(f"Intentando registrar {nombre_replica}...")
            
            # Probar registro inmediatamente para detectar colisiones
            info_test = ServiceInfo(
                type_=tipo_servicio,
                name=f"{nombre_replica}.{tipo_servicio}",
                addresses=[socket.inet_aton(ip_local)],
                port=puerto_local,
                properties={
                    "replica-id": str(nro_nodo),
                    "ip": ip_local,
                    "puerto": int(puerto_local)
                },
                server=f"{nombre_replica}.local."
            )
            
            try:
                zeroconf.register_service(info_test, allow_name_change=False)#False impide que se haya duplicidad de nombres
                print(f"✅ Registro exitoso como {nombre_replica}")
                return nro_nodo, nombre_replica, info_test
            except Exception as reg_error:
                print(f"❌ Colisión detectada para {nombre_replica}: {reg_error}")
                # Continúa al siguiente intento
                continue
                
        except Exception as e:
            print(f"Error en intento {intento + 1}: {e}")
    
    raise Exception("No se pudo obtener un ID único después de múltiples intentos")

if __name__ == "__main__":

    logger = ConsoleLogger("MainReplica", "INFO")

    # ---------- Configuración ----------
    tipo_servicio = "_replica._tcp.local."
    ip_local = socket.gethostbyname(socket.gethostname())
    puerto_local = obtener_puerto_libre()
    max_replicas = 3
    zeroconf = Zeroconf()

    # ---------- Listener ----------
    class ReplicaListener:
        def __init__(self):
            self.replicas = {}

        def add_service(self, zeroconf, tipo, name):
            info = zeroconf.get_service_info(tipo, name)
            if info:
                rid = int(info.properties[b"replica-id"])
                nombre_simple = name.split("._")[0]  # ✅ Extrae solo "replica-2"
                self.replicas[rid] = {
                    "id": rid,
                    "nombre": nombre_simple,
                    "ip": socket.inet_ntoa(info.addresses[0]),
                    "puerto": info.port
                }
                logger.info(f"Detectada réplica: {nombre_simple} (ID {rid})")

        def update_service(self, *args): pass
        def remove_service(self, *args): pass

    # ---------- ID único con retry ----------
    try:
        nro_nodo, nombre_replica, info_local = obtener_id_unico_con_retry(zeroconf, tipo_servicio, ip_local, puerto_local)
        logger.info(f"✅ ID único obtenido: {nro_nodo}, nombre: {nombre_replica}")
    except Exception as e:
        logger.error(f"❌ Error crítico obteniendo ID único: {e}")
        zeroconf.close()
        exit(1)

    # ---------- El registro DNS ya se hizo en la función de retry ----------

    # ---------- Listener principal ----------
    listener = ReplicaListener()
    ServiceBrowser(zeroconf, tipo_servicio, listener)
    time.sleep(1.0)  # Breve pausa para detectar otras réplicas

    # ---------- Instancia local ----------
    Replica_Local = NodoReplica(nro_nodo, ip_local, puerto_local, "Replica", False)
    logger.error(f"Replica_Local: ip:{Replica_Local.host}; puerto{Replica_Local.puerto}")

    # ---------- Esperar réplicas vecinas ----------
    timeout = 15  # segundos
    inicio = time.time()

    while len(listener.replicas) < max_replicas and time.time() - inicio < timeout:
        logger.warning(f"Esperando réplicas... Detectadas: {len(listener.replicas)}")
        time.sleep(1)

    Replicas_Vecinas = list(listener.replicas.values())
    logger.info(f"Réplicas vecinas: {Replicas_Vecinas}")
    logger.info("Iniciando NodoReplica local...")

    # ---------- Lógica de réplica ----------
    logger.info("Registrando replicas")
    for replica in Replicas_Vecinas:
        # Evitar registrar la réplica local
        if replica['id'] == nro_nodo:
            continue

        info = (
            f"id_replica={replica['id']},"
            f"nombre_replica={replica['nombre']},"
            f"ip_replica={replica['ip']},"
            f"puerto_replica={replica['puerto']}"
        )
        Replica_Local.registrar_nodo(
            replica['id'],
            replica['nombre'],
            replica['ip'],
            replica['puerto']
        )
        logger.warning(f"Replica agregada con datos:{info}")

    # ---------- Mantener activo ----------
    logger.info("Iniciando booly de replica")
    Replica_Local.iniciar_eleccion()



    #time.sleep(3)    
    #no lo eliminamos para poder guardar el nombre de la terminal
    # logger.info("Eliminando registro del dns...")
    # zeroconf.unregister_service(info_local)
    # zeroconf.close()
    #logger.info("Iniciando booly de replica")
    #Replica_Local.iniciar_eleccion()
    #Replica_Local.nuevo_iniciar_eleccion()

    

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
