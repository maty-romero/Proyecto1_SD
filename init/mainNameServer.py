import os
import traceback

from Pyro5 import errors

from ServidorNombres.ComunicationHelper import ComunicationHelper
from ServidorNombres.ServidorNombres import ServidorNombres




"""INCORPORAR REGISTRO DE NOMBRE DE LA TERMINAL EN EL DNS"""
if __name__ == "__main__":
    
    NameServ = ServidorNombres(56, True)
    ns = NameServ.verificar_nameserver()

    if not ns:
        try:
            ip_local = ComunicationHelper.obtener_ip_local()
            NameServ.iniciar_nameserver_hilo(ip_local)
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
