import Pyro5.server
from Pyro5 import errors
from Cliente.Utils.ComunicationHelper import ComunicationHelper
from Servidor.Aplicacion.NodoServidor import NodoServidor
from Servidor.Aplicacion.ServidorNombres import ServidorNombres
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Dominio.ServicioJuego import ServicioJuego
"""-Futura implementacion: Para manipular ids, podemos hacer que se registre una lista de nodos en el NS,
    o alguna otra similar para poder incrementar esa id y que cada nodo se identifique de manera unica,
    por ejemplo que al momento del registro el nodo incremente un contador en el nameserver,
    pero si se cae, esto puede que no sea tan util.
    """
if __name__ == "__main__":
    
    #el nameServer existe, y se imprimio en este metodo su info
    ns=ServidorNombres.verificar_nameserver()

    if ns:
        try:
            ip_servidor = ComunicationHelper.obtener_ip_local()
            nodoPrincipal = NodoServidor(1,True)
            Gestor_Singleton = nodoPrincipal.ServicioJuego
            daemon = Pyro5.server.Daemon(host=ip_servidor)

            uri = ComunicationHelper.registrar_objeto_en_ns(
                Gestor_Singleton,
                "gestor.partida",
                daemon,
                ns
                )
            print("Se inicio el Gestor de juego con los siguientes Datos")
            print(f"URI:  {uri}")
            print(f"daemon:  {daemon}")
            daemon.requestLoop()

        except errors.NamingError:
            print("Servidor de nombres no encontrado")
        except errors.CommunicationError:
            print("Error de comunicación con el Servidor de nombres")
        except Exception as e:
            print(f"Error inesperado: {e}")
    else: 
        print("No se puede ejecutar el Servidor, dado que el Servidor de nombres no se esta ejecutando. ")