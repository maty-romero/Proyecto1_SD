import Pyro5.api

@Pyro5.api.expose
class Servidor:
    def __init__(self):
        self.respuestas = {}  # {ip_cliente: palabra}

    def enviar_palabra(self, palabra):
        # Obtener IP del cliente que hace la llamada
        client_ip = Pyro5.api.current_context.client.sock.getpeername()[0]

        # Guardar la palabra usando la IP como clave
        self.respuestas[client_ip] = palabra
        
        # Devolver las palabras de los demás clientes
        print(f"Desde Server: Client: {client_ip} | Envio: {palabra} | Count Dict: {len(self.respuestas)}")
        all_words_str = "\n".join(f"{ip}: {pal}" for ip, pal in self.respuestas.items())
        
        return all_words_str

def main():
    # Crear daemon en la IP accesible desde la red
    ip = "10.15.0.214"
    daemon = Pyro5.api.Daemon(host=ip)
    ns = Pyro5.api.locate_ns(host=ip, port=9090)

    # Registrar el objeto
    uri = daemon.register(Servidor())
    ns.register("ServidorPalabras", uri)

    print("Servidor listo")
    daemon.requestLoop()


if __name__ == "__main__":
    main()
