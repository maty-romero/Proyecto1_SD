import sys, time, socket
from zeroconf import Zeroconf, ServiceBrowser, ServiceInfo

from Servidor.Aplicacion.NodoReplica import NodoReplica
from Servidor.Aplicacion.Nodo import Nodo

NODOS_IDS = [1, 2, 3, 4, 5]
servicios = {}

class Listener:
    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info:
            nid = int(name.split('-')[1].split('.')[0])
            servicios[nid] = (socket.inet_ntoa(info.addresses[0]), info.port)
            print(f"[Zeroconf] Descubierto Nodo {nid} en puerto {info.port}")

my_id = int(sys.argv[1])

# Asignar puerto dinámico
sock_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_temp.bind(("127.0.0.1", 0))
my_port = sock_temp.getsockname()[1]
sock_temp.close()

print(f"[Main] Puerto asignado: {my_port}")

# Registrar mi propio servicio
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
time.sleep(3)

# Construir lista de nodos
lista_nodos = [Nodo(nid, f"n{nid}", servicios[nid][0], servicios[nid][1]) 
               for nid in NODOS_IDS if nid in servicios]

# Calcular el mayor ID entre los nodos descubiertos
max_id = max([n.id for n in lista_nodos] + [my_id])

# El nodo con id máximo será el coordinador
es_coordinador = (my_id == max_id)

my_ip = "127.0.0.1"
app = NodoReplica(my_id, f"n{my_id}", my_ip, my_port, lista_nodos, es_coordinador)
app.iniciar()
print(f"[Nodo {my_id}] corriendo en {my_ip}:{my_port}, coordinador={es_coordinador}")
try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    app.manejador.parar_escucha()
    zc.unregister_service(mi_servicio)
    zc.close()