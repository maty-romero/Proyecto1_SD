# --- Servidor ---
import Pyro5.api

@Pyro5.api.expose
class Servidor:
    def __init__(self):
        self.clientes = []

    def registrar_cliente(self, cliente_uri):
        cliente = Pyro5.api.Proxy(cliente_uri)
        self.clientes.append(cliente)

    def enviar_a_todos(self, msg):
        for c in self.clientes:
            try:
                c.recibir_mensaje(msg)
            except:
                print("Error con un cliente")

daemon = Pyro5.api.Daemon()
ns = Pyro5.api.locate_ns()
uri = daemon.register(Servidor)
ns.register("Servidor", uri)

print("Servidor listo")
daemon.requestLoop()
