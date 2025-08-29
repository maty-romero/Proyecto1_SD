import Pyro5.api
import subprocess #consultar que tan factible es, puede tambien crearse un .bat
import time
import sys
from Nodo import Nodo
from Pyro5 import errors
from builtins import ConnectionRefusedError
import threading
import time
import Pyro5.nameserver

"""FALTA INCORPORAR IMPLEMENTACION SINGLETON A LA CLASE"""
class ServidorDeNombres:

    def verificar_nameserver(self):
        """Verifica si el servidor de nombres esta disponible"""
        try:
            Pyro5.api.locate_ns()
            return True
        except (errors.NamingError, errors.CommunicationError, ConnectionRefusedError) as e:
            print(f"No se pudo conectar al servidor de nombres: {e}")
            return False

    def iniciar_subproceso_nameserver(self):
        """Intenta iniciar el nameserver si no está disponible"""
        if self.verificar_nameserver():
            print("El servidor de nombres ya está ejecutándose")
            return True
        print("Iniciando el servidor de Nombres...")
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "Pyro5.nameserver"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            time.sleep(3)
            return self.verificar_nameserver()
        except Exception as e:
            print(f" Error al iniciar el servidor de nombres: {e}")
            return False

    @staticmethod
    def iniciar_nameserver_hilo(host_ip: str):
        """Inicia el servidor de nombres en un hilo daemon."""
        def ns_loop():
            print(f"[Servidor de Nombres] Iniciando en {host_ip}...")
            Pyro5.nameserver.start_ns_loop(host=host_ip)
            print("[Servidor de Nombres] Detenido.")

        hilo = threading.Thread(target=ns_loop)
        hilo.daemon = True
        hilo.start()
        time.sleep(1)  # Espera a que el NS esté listo