from Servidor.Comunicacion.ManejadorSocket import ManejadorSocket
from Servidor.Utils.ConsoleLogger import ConsoleLogger


class ServicioComunicacion:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.sockets_registrados: ManejadorSocket = []
        self.logger = ConsoleLogger()
        #self.clientes: ClienteConectado = {}  # {id_cliente: manejador_socket}

    # Metodos de Suscripcion
    def suscribir_cliente(self, id_cliente, manejador_socket):
        pass
        # self.clientes[id_cliente] = manejador_socket

    def desuscribir_cliente(self, id_cliente):
        pass
        # self.clientes.pop(id_cliente, None)

    def enviar_a_cliente(self, id_cliente, mensaje):
        pass
        # if id_cliente in self.clientes:
        # self.clientes[id_cliente].enviar(mensaje)

    def broadcast(self, mensaje):
        pass
        # for cliente in self.clientes.values():
        # cliente.enviar(mensaje)

    def replicar_bd(self, datos):
        pass
        # Podrías tener un grupo especial de "nodos réplica"
        # for cliente_id, cliente in self.clientes.items():
        # if cliente_id.startswith("replica"):
        # cliente.enviar(datos)

    def llamada_rpc(self, id_cliente, metodo, *args, **kwargs):
        pass

