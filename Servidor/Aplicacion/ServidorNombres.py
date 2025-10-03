import Pyro5.api
import subprocess
import sys
import time
import threading
from Pyro5 import errors
from builtins import ConnectionRefusedError
import Pyro5.nameserver

from Servidor.Aplicacion.Nodo import Nodo


class ServidorNombres(Nodo):
    """Servidor de Nombres basado en Pyro5, con soporte para ejecución en hilo o subproceso."""

    def __init__(self, id, nombre="NameServer", activo=False):
        super().__init__(id, nombre, activo)
        self.ns_proceso = None  # Guardamos el proceso externo si se usa subproceso

    # ------------------------------------------------------------------
    @staticmethod
    def verificar_nameserver(timeout: int = 2):
        """Intenta localizar un NameServer disponible en la red local."""
        try:
            ns = Pyro5.api.locate_ns()
            objetos = ns.list()
            print("[NameServer] Disponible. Objetos registrados:", flush=True)
            for nombre, uri in objetos.items():
                print(f" - {nombre}: {uri}", flush=True)
            return ns
        except (errors.NamingError, errors.CommunicationError, ConnectionRefusedError):
            return None

    # ------------------------------------------------------------------
    def iniciar_nameserver_subproceso(self, timeout: int = 5):
        """Inicia el NameServer como un subproceso externo."""
        if self.verificar_nameserver():
            print("  El NameServer ya está en ejecución", flush=True)
            return True

        print("[NameServer] Iniciando en subproceso...", flush=True)
        try:
            self.ns_proceso = subprocess.Popen(
                [sys.executable, "-m", "Pyro5.nameserver"],
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )

            for _ in range(timeout):
                if self.verificar_nameserver():
                    print(" NameServer iniciado correctamente (subproceso)", flush=True)
                    return True
                time.sleep(1)

            print(" Timeout esperando al NameServer.", flush=True)
            return False

        except Exception as e:
            print(f" Error al iniciar el NameServer en subproceso: {e}", flush=True)
            return False

    # ------------------------------------------------------------------
    def detener_nameserver(self):
        """Detiene el NameServer si fue lanzado por este proceso."""
        if self.ns_proceso and self.ns_proceso.poll() is None:
            print(" Deteniendo NameServer...", flush=True)
            self.ns_proceso.terminate()
            self.ns_proceso.wait()
            print(" NameServer detenido.", flush=True)

    # ------------------------------------------------------------------
    def iniciar_nameserver_hilo(self, host_ip: str, timeout: int = 5):
        """Inicia el NameServer en un hilo daemon y espera hasta que esté disponible."""

        def ns_loop():
            print(f"[NameServer] Iniciando en {host_ip}...", flush=True)
            Pyro5.nameserver.start_ns_loop(host=host_ip)

        # Arrancar en hilo separado
        hilo = threading.Thread(target=ns_loop, daemon=True)
        hilo.start()

        # Esperar a que esté disponible
        for _ in range(timeout):
            if self.verificar_nameserver():
                print(" NameServer iniciado correctamente (hilo)", flush=True)
                return True
            time.sleep(1)

        print(" Timeout esperando al NameServer (hilo).", flush=True)
        return False
