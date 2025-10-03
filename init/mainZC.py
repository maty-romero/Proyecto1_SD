import sys, time, socket
from zeroconf import Zeroconf, ServiceBrowser, ServiceInfo
from Servidor.Aplicacion.Nodo import Nodo
from Servidor.Aplicacion.NodoReplica import NodoReplica
from Utils.ComunicationHelper import ComunicationHelper 

NODOS_IDS = [1, 2, 3, 4, 5]
# Mapeo de ID a puerto fijo
PUERTOS_FIJOS = {
    1: 7001,
    2: 7002,
    3: 7003,
    4: 7004,
    5: 7005
}
servicios = {}

class Listener:
    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info:
            nid = int(name.split('-')[1].split('.')[0])
            servicios[nid] = (socket.inet_ntoa(info.addresses[0]), info.port)
            #print(f"[Zeroconf] Descubierto Nodo {nid} en puerto {info.port}")

    def remove_service(self, zc, type_, name):
        pass

    def update_service(self, zc, type_, name):
        pass

id_nodo = int(sys.argv[1])
puerto_nodo = PUERTOS_FIJOS[id_nodo]
ip_nodo = ComunicationHelper.obtener_ip_local()
print(f"[Main] Datos de nodo local: {id_nodo}|{ip_nodo}:{puerto_nodo}")

# Registrar servicio propio en DNS
zc = Zeroconf()
mi_servicio = ServiceInfo(
    "_nodo._udp.local.",
    f"nodo-{id_nodo}._nodo._udp.local.",
    addresses=[socket.inet_aton(ip_nodo)],
    port=puerto_nodo,
    properties={"id": str(id_nodo)}
)
#si el servicio ya estaba registrado lo borra
try:
    zc.unregister_service(mi_servicio)
except Exception:
    pass
zc.register_service(mi_servicio)

# Buscar otros servicios
ServiceBrowser(zc, "_nodo._udp.local.", Listener())

# ESPERAR 8 SEGUNDOS para recibir lista actualizada
print(f"[Main] Esperando 3 segundos para descubrir otros nodos...")
time.sleep(3)

# Construir lista de nodos
lista_nodos = [Nodo(id=nid, nombre=f"n{nid}", host=servicios[nid][0], puerto=servicios[nid][1])
               for nid in NODOS_IDS if nid in servicios]

print(f"[Main] Nodos Registrados:")
for n in lista_nodos:
    print(f"  - Nodo {n.id}: {n.nombre} en {n.host}:{n.puerto}")

# Calcular el mayor ID entre los nodos descubiertos
max_id = max([n.id for n in lista_nodos] + [id_nodo])

# El nodo con id máximo será el coordinador
es_coordinador = (id_nodo == max_id)

print(f"[Main] El nodo [{id_nodo}] es coordinador: {es_coordinador}")
print(f"[Main] Iniciando aplicación...")

# AHORA SÍ SE INICIA EL CÓDIGO
app = NodoReplica(id=id_nodo, host=ip_nodo, puerto=puerto_nodo, lista_nodos=lista_nodos, nombre=f"n{id_nodo}", esCoordinador=es_coordinador)
app.iniciar()

try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    app.manejador.parar_escucha()
    zc.unregister_service(mi_servicio)
    zc.close()