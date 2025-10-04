# ---------------- ServicioComunicacion ----------------
import threading
import time
from datetime import UTC, datetime

import Pyro5
from Servidor.Comunicacion.ClienteConectado import ClienteConectado
from Servidor.Aplicacion.Nodo import Nodo
from Utils.ConsoleLogger import ConsoleLogger
from Utils.SerializeHelper import SerializeHelper
from Utils.ManejadorSocket import ManejadorSocket

class ServicioComunicacion:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.logger = ConsoleLogger(name="ServicioComunicacion", level="INFO")
        self.clientes: list[ClienteConectado] = []
        self.clientes_caidos: list[ClienteConectado] = []
        self.nodos_cluster: list[Nodo] = []  # nodos replicas
        
        # NOTA: _restaurar_clientes_persistidos() se llama desde NodoReplica.iniciar_como_coordinador()
        # después de que todos los servicios estén registrados
        
        threading.Thread(target=self._loop_verificacion_clientes, daemon=True).start()

    # ---------------- Clientes ----------------
    def listado_nicknames(self) -> list[str]:
        return [c.nickname for c in self.clientes]

    def hay_lugar_disponible(self, max_jugadores: int) -> bool:
        return len(self.clientes) < max_jugadores

    def is_nickname_disponible(self, nickname: str) -> bool:
        return not any(c.nickname == nickname for c in self.clientes)

    def suscribir_cliente(self, nickname, nombre_logico, ip_cliente, puerto_cliente, uri_cliente):
        # Verificar si ya existe un cliente con ese nickname
        for cliente in self.clientes:
            if cliente.nickname == nickname:
                self.logger.error(f"Cliente '{nickname}' ya está registrado. Ignorando duplicado.")
                return

        cliente = ClienteConectado(nickname, nombre_logico, ip_cliente, puerto_cliente, uri_cliente)
        cliente.socket.conectar_a_nodo(ip_cliente, puerto_cliente)
        self.clientes.append(cliente)
        
        self.logger.info(f"Cliente '{nickname}' registrado y conectado")

    def _verificar_clientes(self):
        activos = []
        for cliente in self.clientes:
            if cliente.esta_vivo():
                activos.append(cliente)
            else:
                self.logger.info(f"Cliente {cliente.nickname} inactivo. Intentando reconectar...")
                
                # Intentar reconectar antes de eliminar definitivamente
                if self._intentar_reconectar_cliente(cliente):
                    self.logger.info(f"Cliente {cliente.nickname} reconectado exitosamente")
                    activos.append(cliente)
                    continue  # No ejecutar el código de eliminación
                
                self.logger.info(f"Cliente {cliente.nickname} definitivamente desconectado. Eliminando...")
                cliente.socket.cerrar() # Se cierra el socket del cliente
                
                # Eliminar de persistencia
                self._eliminar_cliente_persistido(cliente.nickname)
                
                self.dispatcher.manejar_llamada("juego","eliminar_jugador",cliente.nickname) #Se elimina al jugador
                json = SerializeHelper.serializar(
                    exito=False,
                    msg=f"El jugador '{cliente.nickname}' se ha desconectado"
                )
                self.broadcast_a_clientes(json)
        self.clientes = activos # se sobreescribe la lista
        self.logger.info(f"** Numero de Clientes Vivos = {len(self.clientes)}")

    def _intentar_reconectar_cliente(self, cliente: ClienteConectado) -> bool:
        """Intenta reconectar con un cliente que parece haber perdido conexión"""
        try:
            self.logger.info(f"Intentando reconectar con cliente {cliente.nickname} en {cliente.ip_cliente}:{cliente.puerto_cliente}")
            # Cerrar la conexión existente de forma segura
            try:
                if hasattr(cliente.socket, 'cerrar'):
                    cliente.socket.cerrar()
            except Exception as close_error:
                self.logger.warning(f"Error cerrando socket anterior: {close_error}")
            cliente.socket = ManejadorSocket(
                host=cliente.ip_cliente, 
                puerto=cliente.puerto_cliente, 
                nombre_logico=cliente.nickname
            )
            cliente.socket.set_callback(cliente._procesar_mensaje)
            
            # Intentar conectar al cliente (que debería estar esperando)
            cliente.socket.conectar_a_nodo(cliente.ip_cliente, cliente.puerto_cliente)
            
            # Esperar un momento para que se establezca la conexión
            time.sleep(1)
            
            if cliente.socket.conexiones and len(cliente.socket.conexiones) > 0:
                cliente.conectado = True
                cliente.timestamp = datetime.now(UTC)
                self.logger.info(f"Reconexión exitosa con {cliente.nickname}")
                self._enviar_notificacion_recuperacion(cliente)
                return True
            else:
                self.logger.warning(f" No se pudo establecer conexión con {cliente.nickname}")
                return False
                
        except Exception as e:
            self.logger.error(f" Error intentando reconectar con {cliente.nickname}: {e}")
            return False
            
    def _enviar_notificacion_recuperacion(self, cliente: ClienteConectado):
        """Envía notificación de recuperación de servidor al cliente"""
        try:
            mensaje_recuperacion = SerializeHelper.serializar(
                True, 
                "servidor_recuperado", 
                {"mensaje": "Servidor recuperado y funcionando correctamente"}
            )
            cliente.socket.enviar(mensaje_recuperacion)
            self.logger.info(f"Notificación de recuperación enviada a {cliente.nickname}")
        except Exception as e:
            self.logger.error(f"Error enviando notificación de recuperación a {cliente.nickname}: {e}")


    def _eliminar_cliente_persistido(self, nickname: str):
        """Elimina cliente de la persistencia en BD"""
        try:
            # Eliminar de BD
            self.dispatcher.manejar_llamada("db","eliminar_jugador",nickname)
            
        except Exception as e:
            self.logger.error(f"Error eliminando cliente persistido {nickname}: {e}")


    def restaurar_clientes_desde_bd(self) -> int:
        """Restaura clientes confirmados desde la base de datos (guardados por ServicioJuego)"""
        try:
            self.logger.warning("Iniciando restauración de clientes desde BD...")
            
            clientes_bd = self.dispatcher.manejar_llamada("db","obtener_clientes_conectados")
            if not clientes_bd:
                self.logger.info("No hay clientes en BD para restaurar")
                return 0
            self.logger.warning(f"Restaurando {len(clientes_bd)} clientes desde BD...")
            
            # Usar threading para restaurar clientes en paralelo
            import threading
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            clientes_restaurados = 0
            lock_clientes = threading.Lock()  # Para acceso thread-safe a self.clientes y contador
            
            def restaurar_cliente_hilo(cliente_bd):
                """Restaura un cliente en hilo separado"""
                nonlocal clientes_restaurados

                if self._intentar_restaurar_cliente_bd_paralelo(cliente_bd, lock_clientes):
                    with lock_clientes:
                        clientes_restaurados += 1
                    return True
                else:
                    # Si no se puede reconectar, eliminarlo de BD
                    nickname = cliente_bd.get('nickname', 'unknown')
                    self.logger.warning(f"Cliente {nickname} no responde - eliminando de BD")
                    try:
                        self.dispatcher.manejar_llamada("db","eliminar_jugador", nickname)
                    except Exception as e:
                        self.logger.error(f"Error eliminando cliente {nickname} de BD: {e}")
                    return False
            
            with ThreadPoolExecutor(max_workers=min(len(clientes_bd), 5)) as executor:
                # Enviar todos los trabajos
                future_to_cliente = {
                    executor.submit(restaurar_cliente_hilo, cliente_bd): cliente_bd 
                    for cliente_bd in clientes_bd
                }
                
                # Esperar a que todos terminen
                for future in as_completed(future_to_cliente, timeout=30):
                    cliente_bd = future_to_cliente[future]
                    try:
                        resultado = future.result()
                        nickname = cliente_bd.get('nickname', 'unknown')
                        if resultado:
                            self.logger.info(f" Restauración de {nickname} completada exitosamente")
                        else:
                            self.logger.warning(f" Falló restauración de {nickname}")
                    except Exception as e:
                        nickname = cliente_bd.get('nickname', 'unknown')
                        self.logger.error(f" Error en hilo de restauración de {nickname}: {e}")
            
            self.logger.info(f" Restauración paralela completada: {clientes_restaurados}/{len(clientes_bd)} clientes")
            return clientes_restaurados
            
        except Exception as e:
            self.logger.error(f"Error restaurando desde BD: {e}")
            return 0


    def _intentar_restaurar_cliente_bd(self, cliente_bd: dict) -> bool:
        """Intenta restaurar un cliente específico desde datos de BD (versión secuencial)"""
        return self._intentar_restaurar_cliente_bd_paralelo(cliente_bd, None)

    def _intentar_restaurar_cliente_bd_paralelo(self, cliente_bd: dict, lock_clientes) -> bool:
        """Intenta restaurar un cliente específico desde datos de BD (versión thread-safe)"""
        try:
            nickname = cliente_bd.get('nickname', 'unknown')
            ip_cliente = cliente_bd.get('ip', '')
            puerto_cliente = cliente_bd.get('puerto', 0)
            uri_cliente = cliente_bd.get('uri', '')
            
            self.logger.info(f"Intentando restaurar cliente {nickname} desde BD...")

            cliente = ClienteConectado(
                nickname,
                f"jugador.{nickname}",  # nombre_logico reconstruido
                ip_cliente,
                int(puerto_cliente),
                uri_cliente
            )
            
            cliente.socket.conectar_a_nodo(ip_cliente, int(puerto_cliente))
            
            # Esperar conexión
            time.sleep(2)
            
            if cliente.socket.conexiones:
                # Thread-safe: agregar cliente a la lista usando lock si está disponible
                if lock_clientes:
                    with lock_clientes:
                        self.clientes.append(cliente)
                else:
                    self.clientes.append(cliente)
                    
                self.logger.info(f" Cliente {nickname} restaurado desde BD exitosamente")
                
                # Notificar al cliente que el servidor se recuperó
                self._notificar_servidor_recuperado(cliente)
                
                return True
            else:
                self.logger.warning(f" No se pudo restaurar cliente {nickname} desde BD - No responde")
                return False
                
        except Exception as e:
            self.logger.error(f"Error restaurando cliente desde BD {cliente_bd.get('nickname', 'unknown')}: {e}")
            return False


    def _notificar_servidor_recuperado(self, cliente: ClienteConectado):
        """Notifica al cliente que el servidor se ha recuperado"""
        try:
            from Utils.SerializeHelper import SerializeHelper
            mensaje = SerializeHelper.serializar(
                exito=True,
                msg="servidor_recuperado",
                datos={"mensaje": "Conexión con servidor restablecida"}
            )
            cliente.socket.enviar(mensaje)
            self.logger.info(f"Notificación de recuperación enviada a {cliente.nickname}")
        except Exception as e:
            self.logger.error(f"Error notificando recuperación a {cliente.nickname}: {e}")

    def _loop_verificacion_clientes(self):
        while True:
            self._verificar_clientes()
            time.sleep(1.5)

    def broadcast_a_clientes(self, mensaje: str):
        for cliente in self.clientes:
            if cliente.esta_vivo():
                cliente.socket.enviar(mensaje)

    # ---------------- Nodos / Réplicas ----------------
    def registrar_nodo(self, nodo: Nodo):
        if nodo not in self.nodos_cluster:
            self.nodos_cluster.append(nodo)
            self.logger.info(f"Nodo {nodo.get_nombre_completo()} registrado en cluster")
            
    def obtener_nodo_por_id(self, id_nodo: int) -> Nodo:
        for nodo in self.nodos_cluster:
            if nodo.id == id_nodo:
                return nodo
        return None

    def obtener_nodos_cluster(self):
        return self.nodos_cluster


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
    
    #METODO PARA PODER OBTENER LOS DATOS DE CONEXION DEL CLIENTE
    def getDatosCliente(self, usuario: str):
        for cliente in self.clientes:
            if usuario == cliente.nickname:
                return cliente
