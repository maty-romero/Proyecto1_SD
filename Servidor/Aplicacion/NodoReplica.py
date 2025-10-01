"""
-Falta implementar hilo de escucha
-Falta implementar metodo que calcule el timeout del servidor

"""
# ---------------- NodoReplica ----------------
import socket
import sys
import threading
import time
from datetime import datetime
from Servidor.Aplicacion.EstadoNodo import EstadoNodo
import Pyro5

from Servidor.Aplicacion.ManejadorUDP import ManejadorUDP
from Utils.ComunicationHelper import ComunicationHelper
from Servidor.Aplicacion.Nodo import Nodo
from Utils.ManejadorSocket import ManejadorSocket
from Servidor.Comunicacion.ServicioComunicacion import ServicioComunicacion
from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Dominio.ServicioJuego import ServicioJuego
from Servidor.Persistencia.ControladorDB import ControladorDB
from Utils.ConsoleLogger import ConsoleLogger
from Servidor.Aplicacion.EstadoNodo import EstadoNodo


class NodoReplica(Nodo):
    def __init__(self, id, host, puerto, lista_nodos, nombre="Replica", esCoordinador=False):
        super().__init__(id=id, host=host, puerto=puerto, nombre=nombre, esCoordinador=esCoordinador)
        self.logger = ConsoleLogger(name=f"Replica-{self.id}", level="INFO")
        self.Dispatcher = Dispatcher()
        self.ServComunic = ServicioComunicacion(self.Dispatcher)
        self.ServDB = ControladorDB()
        self.ServicioJuego = None

        #self.puerto = puerto
        self.lista_nodos = lista_nodos
        self.nodoSiguiente: Nodo = None
        self.nodoAnterior: Nodo = None
        self.recalcular_vecinos()
        self.manejador = ManejadorUDP(owner=self, puerto_local=self.puerto)
        
        """
        self.socket_manager = Manekad(
            host=self.host,
            puerto=self.puerto,
            nombre_logico=self.get_nombre_completo(),
            es_servidor=False
        )
        """

        if self.esCoordinador:
            threading.Thread(target= self.broadcast_datos_DB, daemon=True).start()


    def broadcast_datos_DB(self):
        self.logger.info("Haciendo broadcast a replicas...")
        while True:
            time.sleep(5)
            # Buscar todos los nodos con ID menor al mío
            nodos_menores = [n for n in self.lista_nodos if n.id < self.id]
            
            if not nodos_menores:
                self.logger.info(f"[{self.id}] No hay nodos menores para notificar")
                return
            
            # Enviar mensaje a cada nodo menor
            for nodo in nodos_menores:
                self.logger.info(f"[{self.id}] Enviando ACTUALIZAR_DB a nodo {nodo.id}")
                self.manejador.enviar_mensaje(
                    nodo.host,
                    nodo.puerto,
                    "ACTUALIZAR_DB"
                )
            
            self.logger.info(f"[{self.id}] Notificación completada a {len(nodos_menores)} nodos")
    
    def iniciar(self):
        if self.esCoordinador:
            #Si el nodo es el coordinador, no envia heart ni hay nodoSiguiente
            #False, no es productor
            self.manejador.iniciar_socket(es_productor=not self.esCoordinador)
        else:
            #True, es productor
            self.manejador.iniciar_socket(es_productor=not self.esCoordinador)
            
    def asignar_nodo_siguiente(self, nodo):
        self.nodoSiguiente = nodo

    def asignar_nodo_anterior(self, nodo):
        self.nodoAnterior = nodo


    def recalcular_vecinos(self):
        ids = [n.id for n in self.lista_nodos]
        idx = ids.index(self.id)

        # Siguiente nodo
        siguiente = self.lista_nodos[idx + 1] if idx + 1 < len(self.lista_nodos) else None
        self.asignar_nodo_siguiente(siguiente)

        # Nodo anterior
        anterior = self.lista_nodos[idx - 1] if idx > 0 else None
        self.asignar_nodo_anterior(anterior)

        self.logger.info(f"[{self.id}] siguiente = {siguiente.id if siguiente else 'NINGUNO'}, anterior = {anterior.id if anterior else 'NINGUNO'}")


    def callback_mensaje(self, mensaje):
        tipo = mensaje.get("type")
        sender = mensaje.get("from")
        ip = mensaje.get("ip")
        puerto = mensaje.get("puerto")

        self.logger.info(f"[Nodo {self.id}] MENSAJE RECIBIDO: TYPE: {mensaje}, FROM: {sender}")
        if tipo == "PING":
            try:
                #le tiene que responder al anterior, osea a dos
                self.logger.warning(f"[{self.id}] Recibió PING de {sender}")
                self.logger.info(f"Enviando PONG a ANTERIOR: {self.nodoAnterior.id}, IP:{ip}, Puerto: {puerto}")
                self.manejador.enviar_mensaje(ip,puerto,"PONG")
            except Exception as e: 
                self.logger.error(f"Error al enviar PONG: {e}")
        elif tipo == "NUEVO_ANTERIOR":
            self.nuevo_anterior(sender,ip,puerto)
        
        elif tipo == "ACK_NUEVO_ANTERIOR":
            self.logger.info(f"[{self.id}] Reconexión exitosa con {sender}")

        elif tipo == "ACTUALIZAR_DB":
            self.logger.warning(f"[{self.id}] Solicitud de actualización de DB desde nodo [{sender}]")
            #self.actualizar_db(datos)
            pass

    def on_siguiente_muerto(self):
        self.logger.warning(f"[{self.id}] Siguiente muerto detectado: {self.nodoSiguiente.id if self.nodoSiguiente else 'NINGUNO'}")
        self.nodoSiguiente = None


    def nuevo_Siguiente(self):
        """Busca un nuevo nodo siguiente cuando el actual falla"""
        nodo_caido = self.nodoSiguiente
        self.logger.warning(f"[{self.id}] Nodo siguiente caído: {nodo_caido.id if nodo_caido else 'NINGUNO'}")
        
        # Buscar candidatos con ID mayor
        candidatos = [n for n in self.lista_nodos if n.id > self.id and n.id != (nodo_caido.id if nodo_caido else -1)]
        
        nuevo_sig = None
        for cand in candidatos:
            self.logger.info(f"[{self.id}] Probando con candidato [{cand.id}] ...")
            if self.manejador.ping_directo(cand):
                nuevo_sig = cand
                break
        
        if nuevo_sig:
            # Asignar nuevo siguiente
            self.asignar_nodo_siguiente(nuevo_sig)
            self.esCoordinador = False
            self.logger.info(f"[{self.id}] Nuevo siguiente: {nuevo_sig.id}")
            
            # Notificar al nuevo siguiente
            self.manejador.enviar_mensaje(
                nuevo_sig.host, nuevo_sig.puerto, "NUEVO_ANTERIOR",
                {"nodo_anterior_id": self.id, "host": self.host, "puerto": self.puerto}
            )
            
            # Reiniciar manejador
            self.manejador.parar_escucha()
            time.sleep(0.5)
            self.iniciar()
        else:
            # Soy coordinador
            self.logger.warning(f"[{self.id}] No encontró un nuevo siguiente. Asumiendo rol de COORDINADOR.")
            self.asignar_nodo_siguiente(None)
            self.esCoordinador = True
            self.manejador.parar_escucha()
            time.sleep(0.5)
            self.iniciar()
            self.levantar_nuevo_coordinador() 

    def nuevo_anterior(self, nodo_anterior_id, host, puerto):
        """
        Asigna un nuevo nodo anterior cuando el nodo que me precedía detectó
        la falla de su siguiente (que era mi anterior).
        
        Args:
            nodo_anterior_id: ID del nuevo nodo anterior
            host: IP del nuevo nodo anterior
            puerto: Puerto del nuevo nodo anterior
        """
        self.logger.info(f"[{self.id}] Asignando nuevo nodo anterior: {nodo_anterior_id}")
        
        # Buscar el nodo en la lista existente
        nuevo_ant = None
        for n in self.lista_nodos:
            if n.id == nodo_anterior_id:
                nuevo_ant = n
                break
        
        # Si no está en la lista, crear referencia temporal
        if not nuevo_ant:
            nuevo_ant = Nodo(nodo_anterior_id, f"Nodo-{nodo_anterior_id}", host, puerto)
            self.logger.info(f"[{self.id}] Nodo anterior no estaba en lista, creando referencia temporal")
        
        self.asignar_nodo_anterior(nuevo_ant)
        print(f"[{self.id}] ✓ Nuevo anterior asignado: {nuevo_ant.id}")
        
        # Enviar confirmación
        self.manejador.enviar_mensaje(
            nuevo_ant.host,
            nuevo_ant.puerto,
            "ACK_NUEVO_ANTERIOR"
        )


    def levantar_nuevo_coordinador(self):
        """
        Se invoca cuando este nodo se convierte en coordinador.
        Implementación futura: inicializar servicios de coordinación, etc.
        """
        self.logger.info(f"=============================\nNodo[{self.id}] SE PROCLAMA NUEVO COORDINADOR\n=============================")
        self.logger.warning(f"Nodo[{self.id}] Restableciendo servicios...")

        # Necesario el broadcast de datos a replicas ?? 
        #threading.Thread(target= self.broadcast_datos_DB, daemon=True).start() 

        ns = Pyro5.api.locate_ns() # hacer en un hilo aparte para mas eficiencia? 
        #ns = Pyro5.api.locate_ns(self.host, self.puerto)
        #self.logger.info(f"Servidor de nombres en: {ns}")

        self.ServicioJuego = ServicioJuego(self.Dispatcher)
        self.Dispatcher.registrar_servicio("juego", self.ServicioJuego)
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComunic)
        self.Dispatcher.registrar_servicio("db", self.ServDB)
        self.Dispatcher.registrar_servicio("nodo_ppal", self)

        existe_partida_previa: bool = self.Dispatcher.manejar_llamada("db", "existe_partida_previa") 
        
        """
            1ra vez que hay un coordinador:
                - [No existe collection partida en BD]
                x- Iniciar servicios (DB, Juego, Comunicación)
                x- Registrar en NameServer Objeto Remoto
                - Crear partida inicial en BD

            Si ya hubo un coordinador antes (cambio de coordinador):
                x- Iniciar servicios (DB, Juego, Comunicación) con datos restaurados
                x- Registrar en NameServer Objeto Remoto nuevamente (limpiar tal vez registro previo?? ) 
                - Restaurar ultimo estado de partida desde BD (construccion de objetos)
                - Reconexion con clientes persistidos (se supone socket cliente abierto previamente)
        """


        if not existe_partida_previa:
            datos = {
            "codigo": 1,
            "clientes_Conectados": [],
            "estado_actual": "",
            "letras_jugadas":"",
            "nro_ronda": 0,
            "categorias": ["Nombres", "Animales", "Colores" ,"Paises o ciudades", "Objetos"],
            "letra": "",
            "respuestas": []
            }

            self.ServDB.crear_partida(datos)    

            #daemon = Pyro5.server.Daemon()
            #daemon = Pyro5.server.Daemon(self.host,self.puerto)
            daemon = Pyro5.server.Daemon(socket.gethostbyname(socket.gethostname()))
            uri = ComunicationHelper.registrar_objeto_en_ns(self.ServicioJuego, "gestor.partida", daemon)
            self.logger.info("ServicioJuego registrado correctamente.")

            # Broadcast a replicas?? 

            daemon.requestLoop()

        else:
            self.logger.warning("Partida previa detectada en BD. Restaurando estado...")
            """  
            # Reconstruccion de objetos de la partida desde BD
            #info_partida_completa: dict = self.Dispatcher.manejar_llamada("db", "obtener_datos_partida_completos")
            #clientes_conectados = info_partida_completa.get("clientes_Conectados", [])
            


            #daemon = Pyro5.server.Daemon()
            #daemon = Pyro5.server.Daemon(self.host,self.puerto)
            daemon = Pyro5.server.Daemon(socket.gethostbyname(socket.gethostname()))
            uri = ComunicationHelper.registrar_objeto_en_ns(self.ServicioJuego, "gestor.partida", daemon)
            self.logger.info("ServicioJuego registrado correctamente.")
            
            # Ahora que el objeto Pyro5 está registrado, restaurar clientes persistidos
            self.logger.info("Restaurando clientes persistidos desde BD...")
            self.ServComunic.restaurar_clientes_persistidos() # en un hilo con un wait o join? 

            daemon.requestLoop()
            """
       

        
        
        
        








# ************************************************************

""" VER
        *** Evaluar si va aca o en ServComunicacion
        self.replicas = [] # un servidor posee varias replicas

        def registrar_replica(self, replica):
            self.replicas.append(replica)
            print(f"Replica {replica.id} registrada")

        def propagar_actualizacion(self, datos):
            self.actualizar_estado(datos)
            for replica in self.replicas:
                replica.actualizar_estado(datos)

        def consultar_bd(self, query):
            # Ejecuta una consulta en la base de datos
            pass

        def guardar_estado_en_bd(self):
            # Persiste el estado actual
            pass
"""


    #se invoca este metodo cuando no se detecto 
    # def check_failover(self, main_server):
    #     if not main_server.estado==EstadoNodo.ACTIVO:
    #         self.logger.warning(f"Se detecto fallo en el servidor. Cambiando {self.get_nombre_completo()} a nodo principal")
    #         self.active = True
    #         self.nombre = "Servidor"
    #         self.iniciar_servicio()
    #         self.logger.warning(f"El nuevo nombre de la replica es {self.get_nombre_completo()} ")
    #         # aquí conectarse o sincronizar con el NameServer


    # def sincronizar_con_servidor(self):
    #         estado = self.servidor_ref.obtener_estado()
    #         self.actualizar_estado(estado)

    #puede servir para impresiones en logger, o como registro
    # def actualizar_estado(self, datos):
    #     self.estado.update(datos)
    #     self.logger.info(f"Réplica {self.id} actualizada con datos: {datos}")