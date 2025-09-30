import sys, time
from Script import Nodo, NodoReplica

if len(sys.argv) < 4:
    print("Uso: python main.py <mi_id> <mi_puerto> <lista nodos id:puerto,...>")
    sys.exit(1)

my_id = int(sys.argv[1])
my_port = int(sys.argv[2])
raw_lista = sys.argv[3]
<<<<<<< HEAD

"""parsea el string a boolean"""
cadena = sys.argv[4].lower()
if cadena == "true":
    es_Coordinador = True
elif cadena == "false":
    es_Coordinador = False
else:
    print("corregir valor del parametro")
    sys.exit(1)

=======
raw_val = sys.argv[4] if len(sys.argv) > 4 else "False"  # por si no se pasa argumento
es_coordinador = raw_val.strip().lower() in ("true", "1", "yes", "y")

print(f"[MAIN] es_Coordinador = {es_coordinador}, tipo: {type(es_coordinador)}")
>>>>>>> e94e95eabb49d36329c3d4f044ea147e48a91321

# Parsear lista de nodos
lista_nodos = []
for entry in raw_lista.split(","):
    nid, nport = entry.split(":")
    lista_nodos.append(Nodo(int(nid), f"n{nid}", "127.0.0.1", int(nport)))

# Crear solo un nodo por ejecución
app = NodoReplica(my_id, f"n{my_id}", "127.0.0.1", my_port, lista_nodos,es_coordinador)
app.iniciar()
print(f"[Nodo {my_id}] corriendo en puerto {my_port}. Ctrl+C para detener.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(f"[Nodo {my_id}] Deteniendo...")
    app.manejador.parar_escucha()
