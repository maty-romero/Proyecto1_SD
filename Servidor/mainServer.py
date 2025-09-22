
import Pyro5.server
from Pyro5 import errors

from Cliente.Utils.ComunicationHelper import ComunicationHelper
from Servidor.Aplicacion.NodoServidor import NodoServidor
from Servidor.Aplicacion.ServidorNombres import ServidorNombres
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Dominio.ServicioJuego import ServicioJuego

if __name__ == "__main__":
    import sys

    Serv = ServidorNombres(56)

    print("¿Qué acción querés realizar con el NameServer?")
    print("1. Iniciar NameServer")
    print("2. Detener NameServer")
    print("3. Continuar sin modificar el NameServer")
    opcion = input("Elegí una opción (1/2/3): ").strip()

    if opcion == "2":
        Serv.detener_nameserver()
        print("NameServer detenido manualmente.")
        sys.exit(0)

    if opcion == "1":
        if Serv.iniciar_nameserver_subproceso():
            try:
                print("[MAIN DENTRO DE IF]")
                ip_servidor = ComunicationHelper.obtener_ip_local()
                nodoPrincipal = NodoServidor(1)

                Gestor_Singleton = nodoPrincipal.ServicioJuego
                daemon = Pyro5.server.Daemon(host=ip_servidor)

                uri = ComunicationHelper.registrar_objeto_en_ns(
                    Gestor_Singleton,
                    "gestor.partida",
                    daemon)

                print(f"URI:  {uri}")
                print(f"[Servidor Lógico] Listo y escuchando en {ip_servidor}")
                daemon.requestLoop()

            except errors.NamingError:
                print("Servidor de nombres no encontrado después de iniciarlo")
            except errors.CommunicationError:
                print("Error de comunicación con el Servidor de nombres")
            except Exception as e:
                print(f"Error inesperado: {e}")

            #print("NameServer iniciado correctamente.")
        else:
            print("[Main] No se pudo iniciar el NameServer.")
            sys.exit(1)

    # --------------------------------------------Inicialización del Servidor--------------------------------------------#
    """
    if Serv.verificar_nameserver():
        try:
            ip_servidor = ComunicationHelper.obtener_ip_local()
            nodoPrincipal = NodoServidor(1)

            Gestor_Singleton = nodoPrincipal.ServicioJuego
            daemon = Pyro5.server.Daemon(host=ip_servidor)

            uri = ComunicationHelper.registrar_objeto_en_ns(
                Gestor_Singleton,
                "gestor.partida",
                daemon)

            print(f"URI:  {uri}")
            print(f"[Servidor Lógico] Listo y escuchando en {ip_servidor}")
            daemon.requestLoop()

        except errors.NamingError:
            print("Servidor de nombres no encontrado después de iniciarlo")
        except errors.CommunicationError:
            print("Error de comunicación con el Servidor de nombres")
        except Exception as e:
            print(f"Error inesperado: {e}")
    else:
        print("[Main] No se pudo iniciar el Servidor de nombres")
    """