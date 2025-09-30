#imports
import socket
import threading
import time


#Modificamos la conexion TCP --> A UDP
class Nodo: # La logica esta sin implementar, hay que revisar
    def __init__(self, id, nombre, host, puerto, esCoordinador):
        self.id = id
        self.host = host # uso de ip en pruebas
        self.puerto = puerto # uso de ip en pruebas
        self.nombre = nombre
        self.esCoordinador = esCoordinador #por lo pronto dos estados, o es nodo activo, o no lo es (es replica)
         #si se complejiza funcionalidad, self.estado="activo"-->"inactivo"-->"sincronizando"
        #self.estado = EstadoNodo.ACTIVO#selecciona el estado actual del nodo


class Nodo:
    def __init__(self, productor:bool):
        self.lista_nodos = [] # Listado de objetos Nodos? 
        self.socket_manager = ManejadorUDP(productor=True)
        self.lock = threading.Lock()
    
    def obtener_posicion_listado(self) -> int: 
        with self.lock():
            return len(self.lista_nodos) + 1 
     
    def obtener_listado_actual(self):
        with self.lock():
            return self.lista_nodos
    
    

import socket
import threading
import json

# La entidad nodo actualiza y lee la lista de siguientes y anterior nodo y luego usa el ManejadorUDP?
class ManejadorUDP:
    def __init__(self, productor:bool):
        # self.owner: Nodo  # Dueño actual de este Manejador UDP 
        self.es_productor = productor # cambiar a es_replica? o es_ppal? 
        self.host = socket.gethostbyname(socket.gethostname()) # 
        self.puerto_local = 9090 # Pasarlo por constructor 
        self.escuchando = False
        self.enviando = False
        self.hilo_escucha = None
        self.hilo_heartbeat = None
        self.socket_local = None
        self.lock = threading.Lock()
        # tipo Nodo ?? No se si esto deberia tenerlo nodo? y solo usar el Manjeador para indicar puerto e ip? 
        self.nodoSiguiente = None 
        self.nodoAnterior = None # Tipo Nodo ?? 

        self.timer = 3
        self.timeout = 9
        self.lock = threading.Lock()


    def asignar_nodo_siguiente(self, nodo: Nodo): 
        
        self.nodoSiguiente = nodo

    def asignar_nodo_anterior(self, nodo: Nodo): 
        self.nodoAnterior = nodo

    def iniciar_socket(self):
        """Inicializa el socket UDP"""
        try:
            if self.es_productor:  
                self.enviando = True
                self.hilo_heartbeat = threading.Thread(target=self._enviar_heartbeat, daemon=True)
            else:  
                self.socket_local = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket_local.bind((self.host, self.puerto_local))
                self.escuchando = True
                print(f"Servidor UDP escuchando en {self.host}:{self.puerto_local}")
                self.hilo_escucha = threading.Thread(target=self.escuchar, daemon=True).start()
        
        # Tendriamos un try catch por cada tipo (productor y no productor)?
        except Exception as e:
            print(f"Error al iniciar el socket UDP: {e}")
            self.escuchando = False
            self.enviando = False
            self.cerrar()  
        
            
    """nodo 2 envia ping/Heart a nodo 1, si excede timeout, busca en la lista menor, sino se levanta coordinador"""
    # Nodo1 <-- Nodo2
    def _enviar_heartbeat(self): # En realidad es PING/PONG no hearbeat
        """Verifica si el coordinador está vivo."""
        while True: 
            time.sleep(5) # sleep + ping.timeout = tiempo que toma descubrir si nodoSig murio  
            if self.nodoSiguiente is not None: # existe nodo sig
                print(f"[{self.id}] Enviando ping a coordinador {self.nodoSiguiente.id}...")
                # Usamos un socket temporal para detectar el fallo
                ping_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                ping_sock.settimeout(2)
                try:
                    msg = json.dumps({"type": "PING", "from": self.id}).encode()
                    ping_sock.sendto(msg, (self.nodoSiguiente.host, self.nodoSiguiente.puerto)) # uso de tupla
                    ping_sock.recvfrom(1024) # Esperar PONG
                except (socket.timeout, socket.gaierror):
                    print(f"Nodo[{self.id}] | El Nodo Siguiente {self.coordinator} no respondió. Iniciando elección.")
                    #self.levantarse_como_coordinador --> CallBack? 
                    
                    # Buscar en lista si nodo actual tendria un siguiente? sino no lo tiene deberia ser el el coordinador? 
                    break # Salir del bucle de heartbeat y esperar nuevo coord.
                finally:
                    ping_sock.close()

    def escuchar(self):
        """Escucha mensajes entrantes por UDP"""
        while self.escuchando:
            try:
                data, addr = self.socket_local.recvfrom(1024)
                mensaje = json.loads(data.decode())
                print(f"Mensaje recibido de {addr}: {mensaje}")
                #self.callback_mensaje(mensaje)
            except Exception as e:
                print(f"Error al recibir datos: {e}")

    def enviar_mensaje(self, ip_destino, puerto_destino, message_type, payload=None):
        """Envía un mensaje a un nodo específico."""
        try:
            # posibles types? --> 'CAMBIOS', 
            # from id ? No hace falta supongo? o deberia mandarlo para que el otro compruebe si el mje es del nodo sig/anterior  
            msg = {"type": message_type, "from": self.id} 
            if payload:
                msg.update(payload)
            #target_host = f"p{target_id}"
            self.sock.sendto(json.dumps(msg).encode(), (ip_destino, puerto_destino))
        except socket.gaierror:
            pass # Ignorar si el host no se puede resolver (proceso caído)

    def callback_mensaje(self, message):
        """Procesa un mensaje recibido."""
        msg_type = message['type']
        sender_id = message['from']

        if msg_type == 'PING':
            print(f"[{self.id}] Recibió PING de {sender_id}")
            #self.send_message(sender_id, 'PONG') -- anterior
            self.enviar_mensaje(sender_id, 'PONG')
            
        
        # TIMEOUT deberia ser luego de enviar el PONG supongo
        # elif msg_type == 'TIMEOUT':
        #     print(f"[{self.id}] Nodo {sender_id} no responde. Iniciando fallback...")
        #     self.fallback_a_nodo_anterior()

        elif msg_type == 'GDB':
            print(f"[{self.id}] Nodo {sender_id} no responde. Iniciando fallback...")
            #ejecuta metodo para guardar en base de datos

        #este mensaje lo recibe solo el nodo siguiente (mayor)
        # elif msg_type == 'COORDINATOR':
        #     nuevo_coord = message['coordinator_id']
        #     self.coordinator = nuevo_coord
        #     print(f"[{self.id}] Nodo {nuevo_coord} es el nuevo coordinador.")


    def restaurar_servicios(self):
        """Restaura servicios como coordinador."""
        print(f"[{self.id}] Restaurando servicios como coordinador...")
        # Aquí iría la lógica para reexponer objetos Pyro, reiniciar servicios de juego, etc.



    # def cerrar(self):
    #     """Cierra el socket UDP"""
    #     print("Cerrando socket UDP...")
    #     self.escuchando = False
    #     with self.lock:
    #         if self.socket_local:
    #             try:
    #                 self.socket_local.close()
    #             except Exception as e:
    #                 print(f"Error al cerrar socket: {e}")
    #             finally:
    #                 self.socket_local = None

    



if __name__ == "__main__":

    """
    ////Opcion de registro de metodos////
    1.Consultar listaNodoMain
    2.Guardar valor devuelto de esa consulta (id asignado)
    3. Cuando todos terminen de asignarse en esa lista, todos consultan la lista final
    4. La lista final es enviada por parametros
    ////Opcion de registro de paginas amarillas////
    1. cada nodo tiene id unica, puerto el mismo, ip unica
    2. Se setean estos valores en cada nodo
    3. Cada nodo se registra en esas paginas amarillas

    La siguiente es la mas viable    
    ////Opcion de registro de lista de tipo nodo////
    1. Nodo uno expone una lista local de 

    """


    pass