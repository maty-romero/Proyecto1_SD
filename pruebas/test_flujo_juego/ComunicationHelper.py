import socket
import threading
import time
import Pyro5.api
import Pyro5.nameserver

class ComunicationHelper:

    @staticmethod
    def obtener_ip_local() -> str:
        """Obtiene la IP local de forma dinámica."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    @staticmethod
    def iniciar_servidor_nombres_en_hilo(host_ip: str):
        """Inicia el servidor de nombres en un hilo daemon."""
        def ns_loop():
            print(f"[Servidor de Nombres] Iniciando en {host_ip}...")
            Pyro5.nameserver.start_ns_loop(host=host_ip)
            print("[Servidor de Nombres] Detenido.")

        hilo = threading.Thread(target=ns_loop)
        hilo.daemon = True
        hilo.start()
        time.sleep(1)  # Espera a que el NS esté listo

    @staticmethod
    def registrar_objeto_en_ns(objeto, nombre_logico: str, daemon: Pyro5.api.Daemon, ns):
        # arg(ns): Pyro5.api.NameServer
        """Registra un objeto remoto en el servidor de nombres."""
        uri = daemon.register(objeto, objectId=f"{nombre_logico}.objeto")

        ns.register(nombre_logico, uri) # ns: Pyro5.api.NameServer
        print(f"[Registro] Objeto '{nombre_logico}' disponible en URI: {uri}")
        return uri
