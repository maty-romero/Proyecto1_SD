import Pyro5.api
import subprocess #consultar que tan factible es, puede tambien crearse un .bat
import sys
import time
from Pyro5 import errors
from builtins import ConnectionRefusedError
import threading

import Pyro5.nameserver

from Servidor.Aplicacion.Nodo import Nodo

"""FALTA INCORPORAR IMPLEMENTACION SINGLETON A LA CLASE"""
class ServidorNombres(Nodo):
    def __init__(self, id,nombre="NameServer",activo=False):
        super().__init__(id,nombre,activo)
        self.ns_proceso = None  # Guardamos el proceso


#Evaluar de llevarlo a utils, o sacarlo de aca
    @staticmethod
    def verificar_nameserver():
        """Verifica si hay algun Name Server en red local"""
        try:
            ns = Pyro5.api.locate_ns()
            objetos = ns.list()
            print("Contenido del NameServer:")
            print(objetos)
            return ns
        except (errors.NamingError, errors.CommunicationError, ConnectionRefusedError) as e:
            print(f"No se pudo conectar al servidor de nombres: {e}")
            return False

    def iniciar_nameserver_subproceso(self):
        """Inicia el NameServer en un subproceso si no está disponible."""
        if self.verificar_nameserver():
            print("El servidor de nombres ya está ejecutándose")
            return True

        print("Iniciando el servidor de nombres...")
        try:
            self.ns_proceso = subprocess.Popen(
                [sys.executable, "-m", "Pyro5.nameserver"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            # Espera activa hasta que el NameServer esté disponible (timeout 10s)
            timeout = 10
            for _ in range(timeout):
                if self.verificar_nameserver():
                    print("NameServer iniciado correctamente")
                    return True
                time.sleep(1)

            print("Timeout esperando al NameServer.")
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


    def iniciar_nameserver_hilo(self, host_ip: str, timeout: int = 10):
        """Inicia el servidor de nombres en un hilo daemon y espera hasta que esté disponible."""
        
        def ns_loop():
            print(f"[Servidor de Nombres] Iniciando en {host_ip}...")
            Pyro5.nameserver.start_ns_loop(host=host_ip)
            print("[Servidor de Nombres] Detenido.")

        # Iniciar el hilo daemon
        hilo = threading.Thread(target=ns_loop)
        hilo.daemon = True  # así el hilo mantiene vivo el NameServer
        hilo.start()
        
        print(f"[Servidor de Nombres] Timeout de {timeout}s esperando al NameServer.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[Servidor de Nombres] Detenido manualmente.")
        return False