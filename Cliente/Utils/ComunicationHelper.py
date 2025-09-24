import socket
from Pyro5 import errors

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
    def registrar_objeto_en_ns(objeto, nombre_logico: str, daemon, ns):#no soporta tipado el ns
        """Registra un objeto remoto en el servidor de nombres."""
        uri = daemon.register(objeto, objectId=f"{nombre_logico}")
        try:
            ns.register(nombre_logico, uri)
        except errors.NamingError as e:
            print(f"[Registro] Error: No se pudo registrar '{nombre_logico}': {e}")
            return None

        print(f"[Registro] Objeto '{nombre_logico}' disponible en URI: {uri}")
        return uri
