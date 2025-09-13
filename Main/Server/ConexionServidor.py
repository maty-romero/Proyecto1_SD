from Main.Common.ConexionBase import ConexionBase
import Pyro5.api

# ConexionServidor.py - Abstrae toda la lógica de comunicación
from Main.Utils.ComunicationHelper import ComunicationHelper

from Main.Common import ManejadorRPC, ManejadorSocket
from Main.Server.Publisher import Publisher


class ClienteConectado:
    def __init__(self, id_cliente, socket, proxy, nick, ip):
        self.id = id_cliente
        self.socket = socket
        self.proxy = proxy
        self.nick = nick
        self.ip = ip
        self.confirmado = bool
        self.timestamp   # Lista de timestamps de actividad
        # Podrías agregar flags como autenticado, en_partida, etc.

    # def enviar(self, mensaje):
    #     self.socket.sendall(mensaje)

class Publisher:

    def __init__(self, ):
        self.clientes: ClienteConectado = []   # Lista o diccionario de clientes conectados
        self.daemon = None

    def suscribir(self, cliente: ClienteConectado):
        self.clientes.append(cliente)
        pass 


request -> gestorPartida -> interfazCompuesta -> ConexionServidor
 -> metodoImpletado (ManejadorRPC o ManejadorSocket)

ManejadorSocket -> ConexionServidor -> interfazCompuesta -> GestorPartida 


Negocio(gestor)<-Aplicacion (nodo)->Comuniacion(Servidor)<->Comuniacion(Cliente)


nodoServidor
    - GestorPartida
    - ConexionServidor


class ConexionServidor(ConexionBase):
    def __init__(self):
        super().__init__()
        self.manejador_rpc = ManejadorRPC()        
        self.manejador_socket = ManejadorSocket()
        self.clientes = []
        self.Publisher = Publisher(self.clientes)
        # getClientes() 

    def verificarClientesVivos()
        # getClientes()
        # recorro list y verifico ClienteConectado.timestamp > fecha_timestamp actual. 

    #registra un cliente en el 
    def registrar_cliente(self, id_cliente, socket, proxy, nick, ip):
        #Se le asigna un puerto disponible, agregar logica
        cli =  ClienteConectado(id_cliente, socket, proxy, nick, ip)
        self.Publisher.suscribir(cli)

    def registrar_objeto(self, gestor, nombre_servicio):
        # Usa ManejadorRPC para los detalles técnicos
        daemon = self.manejador_rpc.inicializar_daemon()
        uri = self.manejador_rpc.registrar_en_nameserver(gestor, nombre_servicio)
        
        # Configurar publisher con los clientes que se conecten
        self.Publisher.configurar_daemon(daemon)
        
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

    #Metodos para persistencia de datos clientes
    def registrar_cliente(self, id_cliente, socket, proxy, nick, ip):
        #Se le asigna un puerto disponible, agregar logica
        self.clientes[id_cliente] = ClienteConectado(id_cliente, socket, proxy, nick, ip)

    def get_cliente(self, id_cliente):
        return self.clientes.get(id_cliente)
