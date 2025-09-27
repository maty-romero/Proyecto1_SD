from concurrent.futures import ThreadPoolExecutor, as_completed
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
    def __init__(self,dispatcher):
        self.dispatcher = dispatcher
        # self.sockets_registrados =  []
        self.logger = ConsoleLogger(name="ServicioComunicacion", level="INFO")
        self.clientes: list[ClienteConectado] = []
        self.nodos_cluster: list[Nodo] = []
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
            time.sleep(1.5)  # cada 2 segundos

    def broadcast(self, mensaje: str):
        if len(self.clientes) <= 0:
            self.logger.warning("Se intenta hacer broadcast sin clientes")
        for cliente in self.clientes:
            if cliente.esta_vivo():
                self.logger.warning(f"Enviando mensaje a cliente'{cliente.nickname}' mediante [SOCKET]")
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
                self.dispatcher.manejar_llamada("juego","eliminar_jugador",cliente.nickname)
                json = SerializeHelper.serializar(
                    exito=False,
                    msg=f"El jugador '{cliente.nickname}' se ha desconectado"
                )
                self.broadcast(json)
        self.clientes = clientes_activos # nos quedamos con clientes vivos
        self.logger.info(f"** Numero de Clientes Vivos = {len(self.clientes)}")

    # Metodos de Suscripcion
    def suscribir_cliente(self, nickname, nombre_logico, ip_cliente, puerto_cliente, uri_cliente):
        cliente = ClienteConectado(nickname, nombre_logico, ip_cliente, puerto_cliente, uri_cliente)
        cliente.socket.conectar() # inicio sesion por socket
        self.clientes.append(cliente)

    # def desuscribir_cliente(self, nickname):
    #     #self.clientes.pop(id_cliente, None)
    #     pass

    """AGREGAR EXCEPCION POR SI CLIENTE DENIEGA CONEXION / NO EXISTE"""

    #No funciona
    # def respuestas_memoria_clientes_ronda(self):
    #     respuestas: dict = {}
    #     for cliente in self.clientes:
    #         try:
    #             proxy = cliente.get_proxy_cliente()
    #             proxy._pyroClaimOwnership()
    #             resp = proxy.obtener_respuesta_memoria()
    #             respuestas[cliente.nickname] = resp
    #         except Pyro5.errors.CommunicationError as e:
    #             self.logger.warning(f"No se pudo obtener respuesta de {cliente.nickname}: {e}")
    #             # opcional: asignar None o valor por defecto
    #             respuestas[cliente.nickname] = None
    #     return respuestas


    # def enviar_datos_para_votacion(self, respuestas_de_clientes):
    #     for cliente in self.clientes:
    #         try:
    #             proxy = cliente.get_proxy_cliente()
    #             proxy._pyroClaimOwnership()
    #             print(f"Enviando datos a: {cliente.nickname}")
    #             proxy.actualizar_vista_votacion(respuestas_de_clientes)
    #         except Pyro5.errors.CommunicationError as e:
    #             self.logger.warning(f"No se pudo enviar datos a {cliente.nickname}: {e}")
    #             continue  # sigue con el siguiente cliente


    # def recolectar_votos(self):
    #     votos_clientes: dict = {}
    #     for i, cliente in enumerate(self.clientes):
    #         try:
    #             proxy = cliente.get_proxy_cliente()
    #             proxy._pyroClaimOwnership()
    #             votos = proxy.obtener_votos_cliente()
    #             votos_clientes[i] = votos
    #         except Pyro5.errors.CommunicationError as e:
    #             self.logger.warning(f"No se pudo obtener votos de {cliente.nickname}: {e}")
    #             votos_clientes[i] = None
    #     return votos_clientes   


    def respuestas_memoria_clientes_ronda(self):
        self.logger.warning("Obteniendo respuestas memoria clientes ronda...")
        respuestas:dict= {}
        for cliente in self.clientes:
            try:
                proxy = cliente.get_proxy_cliente()
                proxy._pyroClaimOwnership()
                resp = proxy.obtener_respuesta_memoria()
                respuestas[cliente.nickname] = resp
            except (Pyro5.errors.CommunicationError, Pyro5.errors.TimeoutError,
                    Pyro5.errors.ConnectionClosedError) as e:
                self.logger.error(f"No se pudo contactar a {cliente.nickname}: {type(e).__name__} - {e}")
                respuestas[cliente.nickname] = {}  # Se toma como respuestas vacias? 
            except Exception as e:
                self.logger.error(f"[ERROR] Fallo inesperado con {cliente.nickname}: {type(e).__name__} - {e}")
                respuestas[cliente.nickname] = {}
            
        return respuestas 


    def enviar_datos_para_votacion(self, respuestas_de_clientes):
        self.logger.warning("Enviando datos votacion (actualizacion vista)...")
        for cliente in self.clientes:
            try:
                proxy = cliente.get_proxy_cliente()
                proxy._pyroClaimOwnership()
                #self.logger.warning(f"Enviando datos a: {cliente.nickname}...")
                proxy.actualizar_vista_votacion(respuestas_de_clientes)

            except (Pyro5.errors.CommunicationError, Pyro5.errors.TimeoutError,
                    Pyro5.errors.ConnectionClosedError) as e:
                self.logger.error(f"No se pudo contactar a {cliente.nickname}: {type(e).__name__} - {e}")
            except Exception as e:
                self.logger.error(f"[ERROR] Fallo inesperado con {cliente.nickname}: {type(e).__name__} - {e}")
    

    def recolectar_votos(self):
        self.logger.warning("Recolectando votos de jugadores...")
        votos_clientes: dict = {}
        for i, cliente in enumerate(self.clientes):
            try:
                proxy = cliente.get_proxy_cliente()
                proxy._pyroClaimOwnership()
                votos = proxy.obtener_votos_cliente()
                votos_clientes[i] = votos

            except (Pyro5.errors.CommunicationError,
                    Pyro5.errors.TimeoutError,
                    Pyro5.errors.ConnectionClosedError) as e:
                self.logger.error(f"No se pudo obtener votos de {cliente.nickname}: {type(e).__name__} - {e}")
                votos_clientes[i] = {}  # Considerar votos vacios? 
            except Exception as e:
                self.logger.error(f"[ERROR] Fallo inesperado con {cliente.nickname}: {type(e).__name__} - {e}")
                votos_clientes[i] = {}

        return votos_clientes
        """
        --> Codigo anterior
        votos_clientes: dict = {}
        for i, cliente in enumerate(self.clientes):
            proxy = cliente.get_proxy_cliente()
            proxy._pyroClaimOwnership()
            votos = proxy.obtener_votos_cliente()
            votos_clientes[i] = votos
        return votos_clientes
        """
    
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
