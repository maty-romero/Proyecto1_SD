import socket
import Pyro5.api


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
    def registrar_objeto_en_ns(objeto, nombre_logico: str, daemon):
        """Registra un objeto remoto en el servidor de nombres."""
        # arg(ns): Pyro5.api.NameServer
        ns = Pyro5.api.locate_ns()
        uri = daemon.register(objeto, f"{nombre_logico}")
        ns.register(nombre_logico, uri) # ns: Pyro5.api.NameServer
        print(f"[Registro] Objeto '{nombre_logico}' disponible en URI: {uri}")
        return uri
