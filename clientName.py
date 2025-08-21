# --- Cliente ---
import Pyro5.api

@Pyro5.api.expose
class ClienteCallback:
    def recibir_mensaje(self, msg):
        print("Servidor dice:", msg)

daemon = Pyro5.api.Daemon()
uri = daemon.register(ClienteCallback)

servidor = Pyro5.api.Proxy("PYRONAME:Servidor")
servidor.registrar_cliente(uri)  # me registro en el servidor

print("Cliente listo...")
daemon.requestLoop()
