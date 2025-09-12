from Main.Common.ConexionBase import ConexionBase
import Pyro5.api

# ConexionServidor.py - Abstrae toda la lógica de comunicación
from Main.Utils.ComunicationHelper import ComunicationHelper

from Main.Common import ManejadorRPC, ManejadorSocket
from Main.Server.Publisher import Publisher

class ConexionServidor(ConexionBase):
    def __init__(self):
        super().__init__()
        self.manejador_rpc = ManejadorRPC()        
        self.manejador_socket = ManejadorSocket()
        self.publisher = Publisher()
    
    def registrar_objeto(self, gestor, nombre_servicio):
        # Usa ManejadorRPC para los detalles técnicos
        daemon = self.manejador_rpc.inicializar_daemon()
        uri = self.manejador_rpc.registrar_en_nameserver(gestor, nombre_servicio)
        
        # Configurar publisher con los clientes que se conecten
        self.publisher.configurar_daemon(daemon)
        
        return uri is not None

    def iniciar_loop(self):
        self.manejador_rpc.iniciar_loop()

    def detener_servidor(self):
        """Detiene el servidor"""
        if self.daemon:
            self.daemon.close()

    #REFACTORIZAR ESTO
    def inicializar_servidor(self, objeto_a_registrar, nombre_objeto: str):
        """Inicializa el daemon y registra el objeto"""
        try:
            self.ip_servidor = ComunicationHelper.obtener_ip_local()
            self.daemon = Pyro5.server.Daemon(host=self.ip_servidor)
            
            # Registrar objeto en el servidor de nombres
            self.uri = ComunicationHelper.registrar_objeto_en_ns(
                objeto_a_registrar,
                nombre_objeto,
                self.daemon
            )
            
            print(f"URI: {self.uri}")
            print(f"[Servidor Lógico] Listo y escuchando en {self.ip_servidor}")
            return True
            
        except Exception as e:
            print(f"Error al inicializar servidor: {e}")
            return False



# class ConexionServidor:
#     def __init__(self):
#         self.daemon = None
#         self.uri = None
#         self.ip_servidor = None
        
#     def inicializar_servidor(self, objeto_a_registrar, nombre_objeto: str):
#         """Inicializa el daemon y registra el objeto"""
#         try:
#             self.ip_servidor = ComunicationHelper.obtener_ip_local()
#             self.daemon = Pyro5.server.Daemon(host=self.ip_servidor)
            
#             # Registrar objeto en el servidor de nombres
#             self.uri = ComunicationHelper.registrar_objeto_en_ns(
#                 objeto_a_registrar,
#                 nombre_objeto,
#                 self.daemon
#             )
            
#             print(f"URI: {self.uri}")
#             print(f"[Servidor Lógico] Listo y escuchando en {self.ip_servidor}")
#             return True
            
#         except Exception as e:
#             print(f"Error al inicializar servidor: {e}")
#             return False
    
#     def iniciar_loop(self):
#         """Inicia el loop de requests del daemon"""
#         if self.daemon:
#             self.daemon.requestLoop()
    
#     def detener_servidor(self):
#         """Detiene el servidor"""
#         if self.daemon:
#             self.daemon.close()