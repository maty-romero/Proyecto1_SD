from NodoServidor import Servidor
from NodoServidorNombres import ServidorNombres
from Nodo import Nodo
import Pyro5.api
from Pyro5 import errors
from ComunicationHelper import ComunicationHelper
from GestorPartida import GestorPartida
from AbstractGUI import AbstractGUI
from ConsoleGUI import ConsoleGUI

if __name__ == "__main__":
   # NodoServ = Nodo(1)#id cualquiera por lo pronto
    Serv = ServidorNombres(None)
    
    #TuttiFruttiServer = TuttiFrutti()
#--------------------------------------------Inicializacion del Servidor--------------------------------------------#
    if Serv.iniciar_nameserver_subproceso():
        try:
            #Se busca ip local
            ip_servidor = ComunicationHelper.obtener_ip_local()
            Gestor_Singleton = GestorPartida(ConsoleGUI())
            daemon = Pyro5.server.Daemon(host=ip_servidor)

            #Se registra el gestor en el servidor de nombres
            uri = ComunicationHelper.registrar_objeto_en_ns(
                Gestor_Singleton,
                "gestor.partida",
                daemon)
            
            print(f"URI:  {uri}")
            print(f"[Servidor Lógico] Listo y escuchando en {ip_servidor}")
            daemon.requestLoop()
            #
        except errors.NamingError:
            print(" Servidor de nombres no encontrado después de iniciarlo")
        except errors.CommunicationError:
            print(" Error de comunicación con el Servidor de nombres")
        except Exception as e:
            print(f" Error inesperado: {e}")
    else:
        print(" No se pudo iniciar el Servidor de nombres")
