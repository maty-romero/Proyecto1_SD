import threading
import time
from datetime import datetime

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
        #threading.Thread(target=self.loop_verificacion(), daemon=True).start()

    def listado_nicknames(self) -> list[str]:
        return [cliente.nickname for cliente in self.clientes]

    def hay_lugar_disponible(self, max_jugadores: int) -> bool:
        return len(self.clientes) < max_jugadores

    def is_nickname_disponible(self, nickname: str) -> bool:
        return not any(cliente.nickname == nickname for cliente in self.clientes)

    def loop_verificacion(self):
        while True:
            self.verificar_clientes()
            time.sleep(15)  # cada 10 segundos

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
                    msg=f"{cliente.nickname} se ha desconectado"
                )
                self.broadcast(json)
        self.clientes = clientes_activos # nos quedamos con clientes vivos

    # Metodos de Suscripcion
    def suscribir_cliente(self, nickname, nombre_logico, ip_cliente, puerto_cliente):
        cliente = ClienteConectado(nickname, nombre_logico, ip_cliente, puerto_cliente)
        cliente.socket.conectar() # inicio sesion por socket
        self.clientes.append(cliente)

    def desuscribir_cliente(self, nickname):
        #self.clientes.pop(id_cliente, None)
        pass

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
