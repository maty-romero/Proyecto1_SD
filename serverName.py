import Pyro5.api

@Pyro5.api.expose
class Servidor:
    def __init__(self):
        # guardamos las palabras registradas por cada cliente
        self.respuestas = {}  # {cliente_id: palabra}

    def enviar_palabra(self, cliente_id, palabra):
        # registramos la palabra del cliente
        self.respuestas[cliente_id] = palabra

        # devolvemos todas las palabras de los demás clientes
        otras_respuestas = {cid: p for cid, p in self.respuestas.items() if cid != cliente_id}
        return otras_respuestas


def main():
    daemon = Pyro5.api.Daemon()         # Crea el daemon
    ns = Pyro5.api.locate_ns()          # Conectarse al NameServer
    uri = daemon.register(Servidor)     # Registrar la clase
    ns.register("ServidorPalabras", uri)

    print("Servidor listo. Esperando clientes...")
    daemon.requestLoop()


if __name__ == "__main__":
    main()
