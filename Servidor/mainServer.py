import time
import traceback
import Pyro5.server
from Pyro5 import errors
from Cliente.Utils.ComunicationHelper import ComunicationHelper
from Cliente.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.NodoServidor import NodoServidor
from Servidor.Aplicacion.ServidorNombres import ServidorNombres
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Dominio.ServicioJuego import ServicioJuego
"""-Futura implementacion: Para manipular ids, podemos hacer que se registre una lista de nodos en el NS,
    o alguna otra similar para poder incrementar esa id y que cada nodo se identifique de manera unica,
    por ejemplo que al momento del registro el nodo incremente un contador en el nameserver,
    pero si se cae, esto puede que no sea tan util.
    """

def medir_tiempo (t1,t2):
    return t2-t1


if __name__ == "__main__":
    
    inicio_time = time.time()
    logger_aux=ConsoleLogger(name="LoggerMain", level="INFO")
    #el nameServer existe, y se imprimio en este metodo su info
    ns=ServidorNombres.verificar_nameserver()

    if ns:
        try:
            ip_servidor = ComunicationHelper.obtener_ip_local()
            logger_aux.warning(f"Tiempo actual desde el inicio (nodo+ip): {medir_tiempo(inicio_time,time.time())}")
            nodoPrincipal = NodoServidor(1,None,True)
            logger_aux.warning(f"Tiempo actual desde el inicio (nodo+ip): {medir_tiempo(inicio_time,time.time())}")  
            Gestor_Singleton = nodoPrincipal.ServicioJuego
            daemon = Pyro5.server.Daemon(host=ip_servidor)
            logger_aux.warning(f"Tiempo actual desde el inicio (daemon+gestor): {medir_tiempo(inicio_time,time.time())}")            
            uri = ComunicationHelper.registrar_objeto_en_ns(
                Gestor_Singleton,
                "gestor.partida",
                daemon,
                ns
                )
            logger_aux.warning(f"Tiempo actual desde el inicio(uri): {medir_tiempo(inicio_time,time.time())}")  
            print("Se inicio el Gestor de juego con los siguientes Datos")
            print(f"URI:  {uri}")
            print(f"daemon:  {daemon}")
            daemon.requestLoop()
            logger_aux.warning(f"Tiempo final: {medir_tiempo(inicio_time,time.time())}")  
        except errors.NamingError:
            print("Servidor de nombres no encontrado")
        except errors.CommunicationError:
            print("Error de comunicación con el Servidor de nombres")
        except Exception as e:
            print(f"Error inesperado: {e}")
            traceback.print_exc()  # esto imprime la traza completa
    else: 
        print("No se puede ejecutar el Servidor, dado que el Servidor de nombres no se esta ejecutando. ")