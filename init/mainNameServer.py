import time
import traceback
from Pyro5 import errors
from ServidorNombres.ComunicationHelper import ComunicationHelper
from ServidorNombres.ServidorNombres import ServidorNombres

if __name__ == "__main__":
    try:
        print("#=============================================================#", flush=True)
        print("   Inicializando Servidor de Nombres... ", flush=True)
        print("#=============================================================#", flush=True)

        NameServ = ServidorNombres(56, True)
        ns = NameServ.verificar_nameserver()

        if ns:
            print(" El Servidor de nombres ya está ejecutándose", flush=True)
        else:
            ip_local = ComunicationHelper.obtener_ip_local()
            NameServ.iniciar_nameserver_hilo(ip_local)
            
            ns = NameServ.verificar_nameserver()
            #segundo if para impresion final
            if ns:
                print("#=============================================================#", flush=True)
                print(f"           Servidor de nombres iniciado en {ip_local}", flush=True)
                print("#=============================================================#", flush=True)
                #Loop para dejar funcionando el ns
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("[Servidor de Nombres] Detenido manualmente.")

    except errors.NamingError:
        print(" Servidor de nombres no encontrado", flush=True)
    except errors.CommunicationError:
        print(" Error de comunicación con el Servidor de nombres", flush=True)
    except Exception as e:
        print(f" Error inesperado: {e}", flush=True)
        traceback.print_exc()

