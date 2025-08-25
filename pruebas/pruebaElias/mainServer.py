from Servidor import Servidor
from Nodo import Nodo
from TuttiFrutti import TuttiFrutti
import Pyro5.api
from Pyro5 import errors

if __name__ == "__main__":
    NodoServ = Nodo(1)#id cualquiera por lo pronto
    Serv = Servidor(NodoServ)
    TuttiFruttiServer = TuttiFrutti()
#--------------------------------------------Inicializacion del Servidor--------------------------------------------#
    if Serv.iniciar_nameserver():
        try:
            daemon = Pyro5.server.Daemon()
            ns = Pyro5.api.locate_ns()
            uri = daemon.register(TuttiFruttiServer)
            ns.register("TuttiFruttiServer", uri)
            print("Servidor iniciado y registrado a la espera de una conexion")
            daemon.requestLoop()
        except errors.NamingError:
            print(" Servidor de nombres no encontrado después de iniciarlo")
        except errors.CommunicationError:
            print(" Error de comunicación con el Servidor de nombres")
        except Exception as e:
            print(f" Error inesperado: {e}")
    else:
        print(" No se pudo iniciar el Servidor de nombres")