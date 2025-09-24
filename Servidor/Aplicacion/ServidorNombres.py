import Pyro5.api
import subprocess #consultar que tan factible es, puede tambien crearse un .bat
import sys
from Pyro5 import errors
from builtins import ConnectionRefusedError
import threading
import time
import Pyro5.nameserver

from Servidor.Aplicacion.Nodo import Nodo

"""FALTA INCORPORAR IMPLEMENTACION SINGLETON A LA CLASE"""
class ServidorNombres(Nodo):
    def __init__(self, id,nombre="NameServer",activo=False):
        super().__init__(id,nombre,activo)
        self.ns_proceso = None  # Guardamos el proceso

    def verificar_nameserver(self):
        """Verifica si el servidor de nombres esta disponible"""
        try:
            Pyro5.api.locate_ns()
            return True
        except (errors.NamingError, errors.CommunicationError, ConnectionRefusedError) as e:
            print(f"No se pudo conectar al servidor de nombres: {e}")
            return False

    def iniciar_nameserver_subproceso(self):
        if self.verificar_nameserver():
            print("El servidor de nombres ya está ejecutándose")
            return True

        print("Iniciando el servidor de Nombres...")
        try:
            self.ns_proceso = subprocess.Popen(
                [sys.executable, "-m", "Pyro5.nameserver"],
                #creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            time.sleep(3)
            return self.verificar_nameserver()
            # Espera activa hasta que el NS esté disponible
            # for _ in range(10):
            #     if self.verificar_nameserver():
            #         return True
            #     time.sleep(1)

            #print("Timeout esperando al NameServer.")
            return False

        except Exception as e:
            print(f"Error al iniciar el servidor de nombres: {e}")
            return False

    def detener_nameserver(self):
        """Finaliza el proceso del NameServer si fue lanzado por este nodo."""
        if self.ns_proceso and self.ns_proceso.poll() is None:
            print("Deteniendo servidor de nombres...")
            self.ns_proceso.terminate()
            self.ns_proceso.wait()
            print("SE HA DETENIDO --> Servidor de nombres.")


    def iniciar_nameserver_hilo(self, host_ip: str):
        """Inicia el servidor de nombres en un hilo daemon."""
        def ns_loop():
            print(f"[Servidor de Nombres] Iniciando en {host_ip}...")
            Pyro5.nameserver.start_ns_loop(host=host_ip)
            print("[Servidor de Nombres] Detenido.")

        hilo = threading.Thread(target=ns_loop)
        hilo.daemon = True
        hilo.start()
        time.sleep(2)  # Espera a que el NS esté listo