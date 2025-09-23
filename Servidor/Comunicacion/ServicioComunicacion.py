import threading
import time
from datetime import datetime
import Pyro5.api
import sys

from Servidor.Comunicacion.ClienteConectado import ClienteConectado
from Servidor.Comunicacion.ManejadorSocket import ManejadorSocket
from Servidor.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Utils.SerializeHelper import SerializeHelper

class ServicioComunicacion:
    def __init__(self):
        # self.dispatcher = dispatcher
        # self.sockets_registrados =  []
        self.logger = ConsoleLogger(name="ServicioComunicacion", level="INFO")
        self.clientes: list[ClienteConectado] = []
        # hilo que maneja verificacion clientes vivos
        threading.Thread(target=self.loop_verificacion, daemon=True).start()

    def listado_nicknames(self) -> list[str]:
        return [cliente.nickname for cliente in self.clientes]

    def hay_lugar_disponible(self, max_jugadores: int) -> bool:
        return len(self.clientes) < max_jugadores

    def is_nickname_disponible(self, nickname: str) -> bool:
        return not any(cliente.nickname == nickname for cliente in self.clientes)

    def loop_verificacion(self):
        while True:
            self.verificar_clientes()
            time.sleep(2)  # cada 2 segundos

    def broadcast(self, mensaje: str):
        for cliente in self.clientes:
            if cliente.esta_vivo():
                self.logger.info(f"Enviando mensaje a cliente'{cliente.nickname}' mediante [SOCKET]")
                cliente.socket.enviar(mensaje)

    def verificar_clientes(self):
        """Verifica clientes vivos y notifica si alguno no lo esta"""
        clientes_activos = []
        for cliente in self.clientes:
            if cliente.esta_vivo():
                clientes_activos.append(cliente)
            else:
                self.logger.info(f"Cliente {cliente.nickname} inactivo. Cerrando sesión.")
                cliente.socket.cerrar()
                json = SerializeHelper.serializar(
                    exito=False,
                    msg=f"El jugador '{cliente.nickname}' se ha desconectado"
                )
                self.broadcast(json)
        self.clientes = clientes_activos # nos quedamos con clientes vivos
        self.logger.info(f"** Numero de Clientes Vivos = {len(self.clientes)}")

    # Metodos de Suscripcion
    def suscribir_cliente(self, nickname, nombre_logico, ip_cliente, puerto_cliente):
        cliente = ClienteConectado(nickname, nombre_logico, ip_cliente, puerto_cliente)
        cliente.socket.conectar() # inicio sesion por socket
        self.clientes.append(cliente)

    def desuscribir_cliente(self, nickname):
        #self.clientes.pop(id_cliente, None)
        pass

    def respuestas_memoria_clientes_ronda(self):
        """
            for in proxyCliente.obtener respuestas
            return dict:
            {
                nickname1: {
                    'categoria1': 'respuesta'
                    'categoria2': 'respuesta'
                },
                nickname2: {
                    'categoria1': 'respuesta'
                    'categoria1': 'respuesta'
                },
            }
        """

        for cliente in self.clientes:
            proxy = self.get_proxy_cliente(cliente)
            print(proxy.obtener_respuesta_memoria())
            
    
    def get_proxy_cliente(self, cliente):
        try:
            proxy_cliente = Pyro5.api.Proxy(f"PYRONAME:{cliente.proxy}")
            return proxy_cliente
        except Pyro5.errors.NamingError:
            self.logger.error(f"Error: No se pudo encontrar el objeto '{cliente.proxy}'.")
            sys.exit(1)
            return None


    """
    def enviar_a_cliente(self, id_cliente, mensaje):
        pass
        # if id_cliente in self.clientes:
        # self.clientes[id_cliente].enviar(mensaje)

    def replicar_bd(self, datos):
        pass
        # Podrías tener un grupo especial de "nodos réplica"
        # for cliente_id, cliente in self.clientes.items():
        # if cliente_id.startswith("replica"):
        # cliente.enviar(datos)

    def llamada_rpc(self, id_cliente, metodo, *args, **kwargs):
        pass
    """
