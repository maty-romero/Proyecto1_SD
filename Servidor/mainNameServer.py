import traceback
from Servidor.Aplicacion.ServidorNombres import ServidorNombres
from Pyro5 import errors

if __name__ == "__main__":

    NameServ = ServidorNombres(56, True)
    ns = NameServ.verificar_nameserver()

    if not ns:
        try:
            NameServ.iniciar_nameserver_subproceso()
            # ip_servidor = ComunicationHelper.obtener_ip_local()
        except errors.NamingError:
            print("Servidor de nombres no encontrado")
        except errors.CommunicationError:
            print("Error de comunicación con el Servidor de nombres")
        except Exception as e:
            print(f"Error inesperado: {e}")
            traceback.print_exc()
    else:
        print("El Servidor de nombres ya está ejecutándose")
