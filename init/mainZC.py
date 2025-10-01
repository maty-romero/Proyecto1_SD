import sys, time, socket
from zeroconf import Zeroconf, ServiceBrowser, ServiceInfo
from Servidor.Aplicacion.Nodo import Nodo
from Servidor.Aplicacion.NodoReplica import NodoReplica

NODOS_IDS = [1, 2, 3, 4, 5]
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

my_id = int(sys.argv[1])

# Asignar puerto dinámico
sock_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_temp.bind(("127.0.0.1", 0))
my_port = sock_temp.getsockname()[1]
sock_temp.close()

print(f"[Main] Puerto asignado: {my_port}")

# Registrar mi propio servicio en DNS
zc = Zeroconf()
mi_servicio = ServiceInfo(
    "_nodo._udp.local.",
    f"nodo-{my_id}._nodo._udp.local.",
    addresses=[socket.inet_aton("127.0.0.1")],
    port=my_port,
    properties={"id": str(my_id)}
)
zc.register_service(mi_servicio)
print(f"[Zeroconf] Registrado Nodo {my_id} en puerto {my_port}")

# Buscar otros servicios
ServiceBrowser(zc, "_nodo._udp.local.", Listener())

# ESPERAR 8 SEGUNDOS para recibir lista actualizada
print(f"[Main] Esperando 8 segundos para descubrir otros nodos...")
time.sleep(8)

# Construir lista de nodos
lista_nodos = [Nodo(id=nid, nombre=f"n{nid}", host=servicios[nid][0], puerto=servicios[nid][1])
               for nid in NODOS_IDS if nid in servicios]

print(f"[Main] Lista de nodos:")
for n in lista_nodos:
    print(f"  - Nodo {n.id}: {n.nombre} en {n.host}:{n.puerto}")

# Calcular el mayor ID entre los nodos descubiertos
max_id = max([n.id for n in lista_nodos] + [my_id])

# El nodo con id máximo será el coordinador
es_coordinador = (my_id == max_id)

my_ip = "127.0.0.1"
print(f"[Main] El nodo [{my_id}] es coordinador: {es_coordinador}")
print(f"[Main] Iniciando aplicación...")

# AHORA SÍ SE INICIA EL CÓDIGO
app = NodoReplica(id=my_id, host=my_ip, puerto=my_port, lista_nodos=lista_nodos, nombre=f"n{my_id}", esCoordinador=es_coordinador)
app.iniciar()

try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    app.manejador.parar_escucha()
    zc.unregister_service(mi_servicio)
    zc.close()