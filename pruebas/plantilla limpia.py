

import socket
import threading

class ManejadorSocket:
    def __init__(self, host, puerto, callback_mensaje):
        self.host = host # Dirección IP del servidor
        self.puerto = puerto    # Puerto del servidor
        self.callback_mensaje = callback_mensaje # Función para manejar mensajes entrantes
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conexion = None
        self.hilo = None
        self._escuchando = False

    def iniciar(self):
        """Inicia el socket y comienza a escuchar un cliente."""
        self.socket.bind((self.host, self.puerto))
        self.socket.listen(1)
        self.conexion, addr = self.socket.accept()
        print(f"Cliente conectado desde {addr}")
        self._escuchando = True
        self.hilo = threading.Thread(target=self._escuchar, daemon=True)
        self.hilo.start()

    def enviar(self, mensaje: str):
        """Envía un mensaje al cliente conectado."""
        if self.conexion:
            self.conexion.sendall(mensaje.encode())

    def _escuchar(self):
        """Loop de escucha en un hilo separado."""
        while self._escuchando:
            try:
                data = self.conexion.recv(1024)
                if not data:
                    break
                self.callback_mensaje(data.decode())
            except OSError:
                break
        self.cerrar()

    def esta_conectado(self) -> bool:
        """Devuelve True si el cliente está conectado."""
        return self.conexion is not None

    def cerrar(self):
        """Cierra la conexión y detiene el hilo."""
        self._escuchando = False
        if self.conexion:
            self.conexion.close()
            self.conexion = None
        self.socket.close()



class ClienteConectado:
        def __init__(self, id_cliente, socket, nombre_logico, nick, ip):
            self.id = id_cliente
            self.socket = socket
            self.proxy = nombre_logico
            self.nick = nick
            self.ip = ip
            self.confirmado = bool
            self.timestamp   # Lista de timestamps de actividad

class ServicioComunicacion:
#---------------------------------------------------------------------------------------------------------------------------------------------------------#

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.sockets_registrados:ManejadorSocket = {}  
        self.clientes:ClienteConectado = {}  # {id_cliente: manejador_socket}

#-------------------------------------------------Metodos de Suscripcion --------------------------------------------------------------------------------------------------------#
    def suscribir_cliente(self, id_cliente, manejador_socket):
        pass
        #self.clientes[id_cliente] = manejador_socket

    def desuscribir_cliente(self, id_cliente):
        pass
        #self.clientes.pop(id_cliente, None)

    def enviar_a_cliente(self, id_cliente, mensaje):
        pass
        #if id_cliente in self.clientes:
            #self.clientes[id_cliente].enviar(mensaje)

    def broadcast(self, mensaje):
        pass
        #for cliente in self.clientes.values():
            #cliente.enviar(mensaje)

    def replicar_bd(self, datos):
        pass
        # Podrías tener un grupo especial de "nodos réplica"
        #for cliente_id, cliente in self.clientes.items():
            #if cliente_id.startswith("replica"):
                #cliente.enviar(datos)

#------------------------------------------------Metodos de llamadas rpc---------------------------------------------------------------------------------------------------------#
    def llamada_rpc(self, id_cliente, metodo, *args, **kwargs):
        pass
        



#------------------------------------------------Servidor ---------------------------------------------------------------------------------------------------------#
class Servidor(Nodo):
    def __init__(self, id, ServComms = ServicioComunicacion(),ServJuego= ServicioJuego()):
        super().__init__(id)    
        self.Dispatcher = Dispatcher()
        self.ServComms = ServicioComunicacion(self.Dispatcher)
        self.ServJuego = ServicioJuego(self.Dispatcher)
        self.ServJuego = ControladorDB()
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComms)
        self.Dispatcher.registrar_servicio("juego", self.ServJuego)
        self.Dispatcher.registrar_servicio("db", self.ServDB)

    def iniciar_servicio(self):
        pass
        #Evaluar si va aca o en ServComunicacion
        #self.replicas = [] # un servidor posee varias replicas
    
    # def registrar_replica(self, replica):
    #     self.replicas.append(replica)
    #     print(f"Replica {replica.id} registrada")

    # def propagar_actualizacion(self, datos):
    #     self.actualizar_estado(datos)
    #     for replica in self.replicas:
    #         replica.actualizar_estado(datos)

    # def consultar_bd(self, query):
    #     # Ejecuta una consulta en la base de datos
    #     pass

    # def guardar_estado_en_bd(self):
    #     # Persiste el estado actual
    #     pass
#------------------------------------------------Servidor ---------------------------------------------------------------------------------------------------------#
class Dispatcher:
    def __init__(self):
        self.servicios = {}
        #self.ServComms = None
        #self.ServDB = None
        #self.ServJuego = None

    def registrar_servicio(self, nombre, servicio):
        self.servicios[nombre] = servicio

    def manejar_llamada(self, id_cliente, nombre_servicio, metodo, datos, **kwargs):

        servicio = self.servicios.get(nombre_servicio)

        if not servicio:
            raise ValueError(f"Servicio {nombre_servicio} no encontrado")

        metodo = getattr(servicio, nombre_servicio, None)
        if not metodo:
            raise ValueError(f"Método {nombre_servicio} no existe en {nombre_servicio}")
        
        return metodo(datos, **kwargs)
#---------------------------------------------------------------------------------------------------------------------------------------------------------#