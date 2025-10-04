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
from Servidor.Dominio.Partida import EstadoJuego
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
        self.Dispatcher = None
        self.ServComunic = None
        self.ServDB = None
        self.ServicioJuego = None

        #self.puerto = puerto
        self.lista_nodos = lista_nodos
        self.nodoSiguiente: Nodo = None
        self.nodoAnterior: Nodo = None
        self.recalcular_vecinos()
        self.manejador = ManejadorUDP(owner=self, puerto_local=self.puerto)
        self.ServDB = ControladorDB(self)
        
        """
        self.socket_manager = Manekad(
            host=self.host,
            puerto=self.puerto,
            nombre_logico=self.get_nombre_completo(),
            es_servidor=False
        )
        """

        if self.esCoordinador:
            #limpiar datos de partida anterior
            self.ServDB.iniciar_nueva_partida()
            self.levantar_nuevo_coordinador()
            #threading.Thread(target= self.broadcast_datos_DB, daemon=True).start()


    def broadcast_datos_DB(self):
        self.logger.error("Haciendo broadcast a replicas...")
        threading.Thread(target=self.hilo_broadcast, daemon=True).start()
        

    def hilo_broadcast(self):
        # Buscar todos los nodos con ID menor a este
        nodos_menores = [n for n in self.lista_nodos if n.id < self.id]  
        if not nodos_menores:
            self.logger.info(f"[{self.id}] No hay nodos menores para notificar")
            return    
         # Obtener datos de MongoDB
        datos = self.ServDB.obtener_datos_partida_completos()
        print(f"""#==================================================================================================#
        RESPUESTAS DE RONDA POR BROADCAST:
        {datos}
        #==================================================================================================#""")

        # Convertir ObjectId a string si es necesario
        if isinstance(datos, list):
            for doc in datos:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
        
        self.logger.info(f"[{self.id}]Se notifico a los nodos replica con los datos: {datos} nodos")

        if not datos:
            self.logger.warning(f"[{self.id}] No hay datos para enviar")
            return
        
        # Formatear el payload
        payload = {"DB": datos}
        # Enviar mensaje a cada nodo menor
        for nodo in nodos_menores:
            self.logger.info(f"[{self.id}] Enviando ACTUALIZAR_DB a nodo {nodo.id}")
            self.manejador.enviar_mensaje(
                nodo.host,
                nodo.puerto,
                "ACTUALIZAR_DB",
                payload
            )
        

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
            self.logger.error(f"[{self.id}] Solicitud de actualización de DB desde nodo [{sender}]")
            datos_partida = mensaje.get("DB")
            self.logger.info(f"Datos de partida recibidos: {datos_partida}")
            #self.Dispatcher.manejar_llamada("db", "actualizar_partida", datos_partida)
            self.ServDB.actualizar_partida(datos_partida)    

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
        self.logger.info(f"\n=============================\nNodo[{self.id}] SE PROCLAMA NUEVO COORDINADOR\n=============================")
        # Lanzar la inicialización de Pyro5 en un hilo separado
        threading.Thread(target=self.hilo_coordinador, daemon=True).start()

    def iniciar_objetos(self):
         #inicializacion de objetos del nodo
        self.Dispatcher = Dispatcher()
        self.ServComunic = ServicioComunicacion(self.Dispatcher)
        self.Dispatcher.registrar_servicio("comunicacion", self.ServComunic)
        self.Dispatcher.registrar_servicio("db", self.ServDB)
        self.Dispatcher.registrar_servicio("nodo_ppal", self)
        self.ServicioJuego = ServicioJuego(self.Dispatcher)
        self.Dispatcher.registrar_servicio("juego", self.ServicioJuego)

    def manejar_estado_partida(self):
        pass
    
    def restaurar_partida_guardada(self):
        pass


    #hilo para levantar el coordinador
    def hilo_coordinador(self):
        """Método que corre en un hilo separado para no bloquear"""
        try:
            self.iniciar_objetos()
            self.manejar_estado_partida()
            # Comprobacion de partidas guardadas
            existe_partida_previa = self.Dispatcher.manejar_llamada("db", "existe_partida_previa")
            self.logger.warning(f"ESTADO de la partida: {self.ServDB.obtener_estado_actual()}")
            if  existe_partida_previa:
                estado = self.ServDB.obtener_estado_actual()
                self.logger.warning(f"Partida previa detectada en BD, en estado:{estado}")
                if estado != "EN_SALA": 
                    self.ServComunic.restaurar_clientes_desde_bd()
                    def inicializar_juego_restaurado():
                        time.sleep(0.5)  # Pequeña pausa para asegurar que daemon esté listo
                        self.ServicioJuego.inicializar_con_restauracion()
                        self.logger.warning("Se restauro una partida previa")
                    
                    hilo_inicializacion = threading.Thread(
                        target=inicializar_juego_restaurado,
                        daemon=True,
                        name="InicializacionJuegoRestaurado"
                    )
                    hilo_inicializacion.start()
            else:
                self.logger.info("No se hallo partida previa para restaurar")
                self.ServDB.iniciar_nueva_partida()
            
            #Termino la inicializacion de la partida, y pasa a ser registrada
            ns = Pyro5.api.locate_ns()
            #si ya existia el servicio, lo borra
            try:
                ns.remove("gestor.partida")
            except Pyro5.errors.NamingError:
                pass

            daemon = Pyro5.server.Daemon(ComunicationHelper.obtener_ip_local())
            #El registrar objeto utiliza overwrite, por lo cual si ya existe el servicio, lo reemplaza
            uri = ComunicationHelper.registrar_objeto_en_ns(self.ServicioJuego, "gestor.partida", daemon)
            self.logger.info(" ---------- ServicioJuego registrado correctamente. ---------- ")
            daemon.requestLoop()
            
        except Exception as e:
            import traceback
            self.logger.error(f"Error inicializando servicios Pyro5: {e}")
            traceback.print_exc()
