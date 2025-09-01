import Pyro5.api
import Pyro5.nameserver
import threading
from gestor_partida import GestorPartida
from strategies import PuntajeSimple

def iniciar_servidor():
    ip_local = "127.0.0.1"
    threading.Thread(target=Pyro5.nameserver.start_ns_loop, args=(ip_local,), daemon=True).start()
    import time; time.sleep(1)

    daemon = Pyro5.api.Daemon(host=ip_local)
    ns = Pyro5.api.locate_ns()
    gestor = GestorPartida(strategy=PuntajeSimple())
    uri = daemon.register(gestor)
    ns.register("gestor.partida", uri)
    print(f"[Servidor] GestorPartida listo en URI: {uri}")
    daemon.requestLoop()

if __name__ == "__main__":
    iniciar_servidor()
