from Main.Server.GestorPartida import GestorPartida
from Main.Server.ConexionServidor import ConexionServidor
from Main.Server.NodoServidorNombres import ServidorNombres
from Main.Common.ConsoleGUI import ConsoleGUI
import Pyro5.errors as errors

if __name__ == "__main__":
   # NodoServ = Nodo(1)#id cualquiera por lo pronto
    Serv = ServidorNombres(None)
    
    #TuttiFruttiServer = TuttiFrutti()
#--------------------------------------------Inicializacion del Servidor--------------------------------------------#
    if Serv.iniciar_nameserver_subproceso():
        try:
            Gestor_Singleton = GestorPartida(ConsoleGUI())
            Conexion = ConexionServidor()
            Conexion_servidor = ConexionServidor()

            if Conexion_servidor.inicializar_servidor(Gestor_Singleton, "gestor.partida"):
                # Iniciar el loop del servidor
                Conexion_servidor.iniciar_loop()
            else:
                print("Error al inicializar el servidor")
        except errors.NamingError:
            print(" Servidor de nombres no encontrado después de iniciarlo")
        except errors.CommunicationError:
            print(" Error de comunicación con el Servidor de nombres")
        except Exception as e:
            print(f" Error inesperado: {e}")
    else:
        print(" No se pudo iniciar el Servidor de nombres")
