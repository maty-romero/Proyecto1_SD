import threading
from threading import Lock, Thread
import time
from collections import defaultdict, Counter

import Pyro5.api

from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Dominio.Jugador import Jugador
from Servidor.Dominio.Partida import Partida
from Servidor.Persistencia.ControladorDB import ControladorDB
from Servidor.Dominio.Partida import EstadoJuego
from Utils.ConsoleLogger import ConsoleLogger
from Utils.SerializeHelper import SerializeHelper
from Servidor.Comunicacion.ClienteConectado import ClienteConectado

@Pyro5.api.expose
class ServicioJuego:
    def __init__(self, dispacher: Dispatcher):
        self.dispacher = dispacher
        self.Partida = Partida()
        self.logger = ConsoleLogger(name="ServicioJuego", level="INFO") # cambiar si se necesita 'DEBUG'
        self.jugadores_min = 1 # pasar por constructor?
        self.logger.info("Servicio Juego inicializado")
        self.Jugadores = {}  # Pasar a OBJETO JUGADOR
        self.lock_confirmacion = Lock()


    def restaurar_partida_desde_bd(self, codigo_partida: int = 1):
        """Restaura el estado de la partida desde la base de datos"""
        try:
            # Obtener datos de la partida desde la BD
            controlador_db: ControladorDB = self.dispacher.manejar_llamada("db", "get_controlador")
            controlador_db.codigo_partida = codigo_partida
            
            datos_partida = controlador_db.obtener_datos_partida_completos()
            if not datos_partida:
                self.logger.warning(f"No se encontró partida con código {codigo_partida}")
                return False
            
            # Restaurar la partida usando el método estático
            self.Partida = Partida.desde_datos_bd(datos_partida)
            
            # Restaurar el diccionario de jugadores para mantener compatibilidad
            self.Jugadores = {}
            for jugador in self.Partida.jugadores:
                self.Jugadores[jugador.nickname] = True  #Si restura el estado que tenían luego de confirmar_jugador
            
            self.logger.info(f"Partida {codigo_partida} restaurada exitosamente")
            self.logger.info(f"Estado: Ronda {self.Partida.nro_ronda_actual}, Jugadores: {list(self.Jugadores.keys())}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restaurando partida: {e}")
            return False


    # confirmar_jugador -> ¿jugadores suficientes? -> iniciar_partida -> inicializar_con_restauracion
    def inicializar_con_restauracion(self, codigo_partida: int = 1): # Para cuando el nodoPrincipal pasa a ser otro y debe restaurar la partida de todos los jugadores - No sirve para cuando 1 solo jugador pierde la porque hace broadcast de nueva_ronda -> se les actualiza a todos la vista
        """TEMPORAL para pruebas de restauración. Inicializa el servicio intentando restaurar desde BD, o crea nueva partida"""
        if self.restaurar_partida_desde_bd(codigo_partida):
            
            # Notificar a clientes conectados sobre el estado actual - TODO mover a otro lado
            if self.Partida.estado_actual == EstadoJuego.EN_SALA:
                self.notificar_estado_sala_a_clientes()
            elif self.Partida.estado_actual == EstadoJuego.RONDA_EN_CURSO:
                self.notificar_ronda_actual_a_clientes()
            elif self.Partida.estado_actual == EstadoJuego.EN_VOTACIONES:
                self.logger.info("🎯 Ejecutando notificación para EN_VOTACIONES")
                self.enviar_respuestas_ronda()
            elif self.Partida.estado_actual == EstadoJuego.MOSTRANDO_RESULTADOS_FINALES:
                self.logger.info("🎯 Ejecutando notificación para MOSTRANDO_RESULTADOS_FINALES")
                self.notificar_resultados_finales_a_clientes()
            else:
                self.logger.warning(f"❌ Estado no reconocido al restaurar: {self.Partida.estado_actual} (tipo: {type(self.Partida.estado_actual)})")
        else:
            self.logger.info("Iniciando con nueva partida") #TEMPORAL si es llamado desde iniciar_partida
            self.Partida = Partida()


    def notificar_estado_sala_a_clientes(self):
        """Envía la información de la sala a todos los clientes"""
        self.logger.info("📤 Enviando mensaje 'info_sala' a clientes")
        info_sala = self.Partida.get_info_sala()
        json = SerializeHelper.serializar(exito=True, msg="info_sala", datos=info_sala)
        self.dispacher.manejar_llamada("comunicacion", "broadcast_a_clientes", json)

    def notificar_ronda_actual_a_clientes(self):
        """Envía la información de la ronda actual a todos los clientes"""
        info_ronda = self.Partida.get_info_ronda()
        json = SerializeHelper.serializar(exito=True, msg="nueva_ronda", datos=info_ronda)
        self.dispacher.manejar_llamada("comunicacion", "broadcast_a_clientes", json)
    
    def notificar_fin_ronda_a_clientes(self):
        """Notifica específicamente el fin de la ronda y desencadena el cambio de vista en clientes"""
        json = SerializeHelper.serializar(exito=True, msg="fin_ronda")
        self.dispacher.manejar_llamada("comunicacion", "broadcast_a_clientes", json)

    def notificar_inicio_votacion_a_clientes(self):
        """Notifica específicamente el inicio de votación"""
        json = SerializeHelper.serializar(exito=True, msg="inicio_votacion")
        self.dispacher.manejar_llamada("comunicacion", "broadcast_a_clientes", json)

    def notificar_datos_votacion_a_clientes(self, info_completa_votacion):
        """Envía los datos específicos para la votación"""
        self.dispacher.manejar_llamada("comunicacion", "enviar_datos_para_votacion", info_completa_votacion)

    def restaurar_estado_votaciones(self):
        """Restaura el estado de votaciones para clientes reconectados (sin transiciones)"""
        self.logger.info("Restaurando estado de votaciones para clientes reconectados")
        
        # Obtener respuestas desde BD
        respuestas_clientes = self.dispacher.manejar_llamada("comunicacion", "respuestas_memoria_clientes_ronda")
        
        # Preparar datos de votación
        info_completa_votacion = self.preparar_datos_votacion(respuestas_clientes)
        
        # Enviar directamente mensaje de estado de votaciones (sin transiciones)
        json = SerializeHelper.serializar(exito=True, msg="estado_votaciones", datos=info_completa_votacion)
        self.dispacher.manejar_llamada("comunicacion", "broadcast_a_clientes", json)

    def notificar_resultados_finales_a_clientes(self):
        """Envía los resultados finales de la partida a todos los clientes"""
        puntajes_totales, ganador = self.Partida.calcular_puntos_partida()
        
        resultados_partida = {
            'jugadores': list(self.Jugadores.keys()),
            'puntajes_totales': puntajes_totales,
            'ganador': ganador
        }
        json = SerializeHelper.serializar(exito=True, msg="fin_partida", datos=resultados_partida)
        self.dispacher.manejar_llamada("comunicacion", "broadcast_a_clientes", json)

    def sincronizar_ronda_con_bd(self):
        """Actualiza todos los datos de la ronda actual en BD"""
        if self.Partida.ronda_actual:
            letra_ronda = self.Partida.ronda_actual.letra_ronda
            nro_ronda = self.Partida.nro_ronda_actual
            self.dispacher.manejar_llamada("db", "actualizar_letra", letra_ronda)
            self.dispacher.manejar_llamada("db", "actualizar_nro_ronda", nro_ronda)
            self.dispacher.manejar_llamada("db", "actualizar_letras_jugadas", self.Partida.letras_jugadas)
            

    def sincronizar_puntajes_con_bd(self):
        """Actualiza los puntajes de todos los jugadores en BD"""
        puntajes_dict = {}
        for jugador in self.Partida.jugadores:
            puntajes_dict[jugador.nickname] = jugador.get_puntaje()
        
        if puntajes_dict:
            modificados = self.dispacher.manejar_llamada("db", "actualizar_puntajes_jugadores", puntajes_dict)
            self.logger.info(f"Puntajes actualizados en BD: {modificados} jugadores")


    def cambiar_estado_partida(self, nuevo_estado):
        """Cambia el estado de la partida y lo guarda en BD"""
        estado_anterior = self.Partida.estado_actual
        self.Partida.set_estado_actual(nuevo_estado)
        # Guardar en BD
        self.dispacher.manejar_llamada("db", "actualizar_estado_partida", nuevo_estado)
        self.logger.info(f"Estado cambiado: {estado_anterior.name} -> {nuevo_estado.name}")


    """
        ServicioJuego --> Entran las llamadas Pyro
    
        Servicios Registrados en NodoServidor --> Dispacher
            - "comunicacion"
            - "db"
        Ejemplo de uso Dispacher: 
            self.Dispatcher.manejar_llamada("comunicacion", "broadcast", "¡Hola a todos!")
        Ejemplo de uso SerializeHelper:
            json = SerializeHelper.serializar(exito=False, msg="", datos={"datos"})
        
    """
    def get_jugadores_minimos(self):
        return  self.jugadores_min

    def obtener_info_sala(self) -> dict:
        return self.Partida.get_info_sala()

    def iniciar_partida(self):
        # Inicia la 1ra Ronda
        #------------Se inicializa la ronda------------------------------------------------#
        #La partida se encuentra en None la primera vez que se vuelve de la votacion, ahi no muestra categorias ni otros datos correctamente
        self.inicializar_con_restauracion() # Por el momento acá, restura o crea nueva partida
        
        if self.Partida.nro_ronda_actual == 0: #Si nro_ronda_actual 0 entonces EstadoJuego.EN_SALA, es decir que empieza una ronda nueva
            self.Partida.iniciar_nueva_ronda() # Ronda 1

            # Actualizar datos en BD
            self.sincronizar_ronda_con_bd()
            
            # Cambiar estado a RONDA_EN_CURSO
            self.cambiar_estado_partida(EstadoJuego.RONDA_EN_CURSO)
            
            #si ya tenemos jugadores en partida, podemos guardar el true o false de la confirmacion ahi mismo. Facilita recuperacion de bd
            jugadores: list[Jugador] = [Jugador(nick) for nick in self.Jugadores.keys()]
            self.Partida.cargar_jugadores_partida(jugadores)

            self.notificar_ronda_actual_a_clientes()
        
        #self.cargarRondaDB(info_ronda)?

    def preparar_datos_votacion(self, respuestas_clientes):
        """Prepara y guarda los datos necesarios para la votación"""
        info_completa_votacion = {
            'nro_ronda': self.Partida.nro_ronda_actual,
            'total_rondas': self.Partida.rondas_maximas,
            'letra_ronda': self.Partida.ronda_actual.letra_ronda,
            'respuestas_clientes': respuestas_clientes
        }

        # Dentro del metodo, se formatea previo a la insercion en BD
        """VER SI ESTA BIEN IMPLEMENTADO --> Guardado en BD y Broadcast a Replicas"""
        self.dispacher.manejar_llamada("db", "reemplazar_respuestas_ronda",
            info_completa_votacion['nro_ronda'], 
            info_completa_votacion['respuestas_clientes']
        )
        
        return info_completa_votacion


    def enviar_respuestas_ronda(self):
        """Finaliza la ronda actual e inicia el proceso de votación"""
        self.notificar_fin_ronda_a_clientes()
        self.notificar_inicio_votacion_a_clientes()

        # Obtener y procesar respuestas
        respuestas_clientes = self.dispacher.manejar_llamada("comunicacion", "respuestas_memoria_clientes_ronda")
        self.Partida.ronda_actual.set_respuestas_ronda(respuestas_clientes)
        
        # Cambiar estado y guardar
        self.cambiar_estado_partida(EstadoJuego.EN_VOTACIONES)
        info_completa_votacion = self.preparar_datos_votacion(respuestas_clientes)
        
        # Enviar datos para votación
        self.notificar_datos_votacion_a_clientes(info_completa_votacion)

        # Broadcast a replcias para actualizacion - VER
        """
        Actualizacion a replicas 
        json = SerializeHelper.serializar(exito=True, msg="info_ronda", datos=info_completa_votacion)
        self.dispacher.manejar_llamada("nodo_ppal", "broadcast_a_nodos", json)
        """

        #Se ejecuta el timer en un hilo separado para no bloquear la llamada remota del cliente que hace STOP
        hilo_timer = threading.Thread(target=self.timer_votacion, daemon=True)
        hilo_timer.start()


    def timer_votacion(self):
        tiempos = [30, 20, 10]
        for t in tiempos:
            mensaje = SerializeHelper.serializar(exito=True, msg="aviso_tiempo_votacion", datos=f"Te quedan {t} segundos para votar")
            self.dispacher.manejar_llamada("comunicacion", "broadcast_a_clientes", mensaje)
            time.sleep(10)

        hilo_pedir_votos = threading.Thread(target=self.obtener_votos_jugadores, daemon=True)
        hilo_pedir_votos.start()
        
        
    def evaluar_ultima_ronda(self):
        if self.Partida.nro_ronda_actual == self.Partida.rondas_maximas:
            self.finalizar_partida()
        else:
            self.Partida.iniciar_nueva_ronda()
            self.cambiar_estado_partida(EstadoJuego.EN_VOTACIONES)
            self.sincronizar_ronda_con_bd()
            self.notificar_ronda_actual_a_clientes()


    def obtener_votos_jugadores(self):
        votos = self.dispacher.manejar_llamada("comunicacion", #Recolectar los votos de la vista
        "recolectar_votos")
        self.procesar_votos_y_asignar_puntaje(votos)



    def procesar_votos_y_asignar_puntaje(self, votos):
        from collections import defaultdict

        respuestas_clientes = self.Partida.ronda_actual.get_respuestas_ronda()
        conteo_respuestas = defaultdict(lambda: defaultdict(int))
        validez = defaultdict(dict)

        # --- Primera pasada: validar respuestas y contar ocurrencias ---
        for jugador, info in respuestas_clientes.items():
            respuestas = info.get("respuestas", {})
            if not respuestas:
                self.logger.warning(f"No hay respuestas registradas para jugador {jugador}")
                continue

            for categoria, respuesta in respuestas.items():
                true_count = false_count = 0
                for ronda, votos_jugadores in votos.items():
                    if jugador in votos_jugadores and categoria in votos_jugadores[jugador]:
                        if votos_jugadores[jugador][categoria]:
                            true_count += 1      
                        else:
                            false_count += 1

                es_valida = (true_count > false_count)
                validez[jugador][categoria] = es_valida

                # Solo cuenta la respuesta si es válida y no vacía
                if respuesta and es_valida:
                    conteo_respuestas[categoria][respuesta] += 1

                self.logger.debug(
                    f"[VALIDACIÓN] {jugador} - {categoria}: '{respuesta}' "
                    f"T:{true_count} F:{false_count} válida:{es_valida}"
                )

        # --- Segunda pasada: asignar puntajes ---
        puntajes = {}
        for jugador, info in respuestas_clientes.items():
            puntajes[jugador] = {}
            respuestas = info.get("respuestas", {})
            if not respuestas:
                self.logger.warning(f"No hay respuestas registradas para jugador {jugador}")
                continue

            for categoria, respuesta in respuestas.items():
                es_valida = validez[jugador].get(categoria, False)
                if not respuesta or not es_valida:
                    puntaje = 0
                else:
                    repeticiones = conteo_respuestas[categoria][respuesta]
                    puntaje = 10 if repeticiones == 1 else 5

                puntajes[jugador][categoria] = puntaje
                self.logger.debug(
                    f"[PUNTAJE] {jugador} - {categoria}: '{respuesta}' "
                    f"válida:{es_valida}, repeticiones:{conteo_respuestas[categoria][respuesta]} "
                    f"=> {puntaje} puntos"
                )

        # --- Totales y asignación ---
        totales = {jugador: sum(categorias.values()) for jugador, categorias in puntajes.items()}

        for jugador in self.Partida.jugadores:
            total = totales.get(jugador.nickname, 0)  # evita KeyError
            jugador.sumar_puntaje(total)
            self.logger.info(f"El puntaje del jugador {jugador.nickname} es {total}")

        # Guardar puntajes actualizados en BD
        self.sincronizar_puntajes_con_bd()

        self.evaluar_ultima_ronda()



    def finalizar_partida(self):
        """Notifica el fin de la partida y envía los datos finales"""
        self.cambiar_estado_partida(EstadoJuego.MOSTRANDO_RESULTADOS_FINALES)
        self.notificar_resultados_finales_a_clientes()

        #------------se resetean los datos de la partida------------------------------------------------#
        self.Partida=self.Partida.crear_nueva_partida()
        for nickname in self.Jugadores:
            self.Jugadores[nickname]= False 
        self.logger.warning("La partida finalizo y se borro su instancia de servicio de juego, Inicie una nueva partida")

        #llegada a esta instancia se limpia la bd, ya no se necesita persistencia de datos
        # self.dispacher.manejar_llamada(
        #     "db",  # nombre_servicio
        #     "limpiar_BD"#,  # nombre_metodo
        #         #json #args
        # )


    # PENDIENTE - Manejar intentos de unirse o acceso en otros estados de la partida
    def solicitar_acceso(self):#(self,nickname)
        #si no existe una partida, se evalua si hay lugar
        # self.logger.info(f"El estado de la PARTIDA es {self.Partida.get_estado_actual()}")
        # if self.Partida.get_estado_actual() == EstadoJuego.RONDA_EN_CURSO:
        #     return SerializeHelper.respuesta(
        #         exito=False,
        #         msg="Ya hay una partida en curso, no puede unirse"
        #     )
        # else:
        #     hay_lugar: bool = self.dispacher.manejar_llamada(
        #         "comunicacion",  # nombre_servicio
        #         "hay_lugar_disponible",  # nombre_metodo
        #         self.jugadores_min  # args
        #     )

        #     if not hay_lugar:
        #         return SerializeHelper.respuesta(
        #             exito=False,
        #             msg="La sala está llena, no puede unirse."
        #         )

            # hay lugar
        return SerializeHelper.respuesta(
            exito=True,
            msg="Hay lugar disponible, puede unirse."
        )
        
        

        """
        if not self.Partida:

        else:#si existe partida es porque se inicio un juego
        #elif nickname in self.Partida.jugadores    # se procede a verificar si existe jugador
            #return SerializeHelper.respuesta(
            #     exito=True,
            #     msg="Hay partida disponible pero ya habias entrado, puedes unirte de nuevo"
            # )
            #aca iria el self
            #En caso de implementar, comentar el siguiente return

            return SerializeHelper.respuesta(
                exito=False,
                msg="Ya hay una partida en curso, no puede unirse"
            )
        """
    def CheckNickNameIsUnique(self, nickname: str):
        is_not_string = not isinstance(nickname, str)

        if (nickname == "" or is_not_string):
            return SerializeHelper.respuesta(
                exito=False,
                msg="NickName vacio o no tiene formato valido"
            )

        formated_nickname = nickname.lower().replace(" ", "")

        is_nickname_disponible: bool = self.dispacher.manejar_llamada(
            "comunicacion", # nombre_servicio
            "is_nickname_disponible", # nombre_metodo
            formated_nickname # args
        )

        # nickname no disponible
        if not is_nickname_disponible:
            return SerializeHelper.respuesta(
                exito=False,
                msg="El nickname ingresado ya esta siendo utilizado"
            )
        # nickname ingresado esta disponible
        self.Jugadores[formated_nickname] = False # False = no confirmado

        return SerializeHelper.respuesta(exito=True, msg="NickName disponible")

    def unirse_a_sala(self, info_cliente: dict):#falta atajar reconexion en este metodo!! 
        """
        1. Verificar si existe ya jugador en sala ???
        2. Suscribir / Registrar Jugador
        3. Conectarse al socket del Cliente (se hace al suscribir cliente)
        4. Notificar entrada de nuevo a todos los jugadores (broadcast)
        5. Obtener info Sala
        6. Retornar info Sala via Pyro
        """
        #si existe la partida, y pudo unirse a sala, es porque se le permitio el acceso
        #if self.Partida
            #self.Jugadores.append[info_cliente['nickname'],True]
            # return SerializeHelper.respuesta(
            #     exito=True,
            #     msg="Has vuelto a unirte a la partida, bienvenido",
            #     datos=info_sala
            # )
        try:
            nickname = info_cliente['nickname']
            nombre_logico = info_cliente['nombre_logico']
            ip_cliente = info_cliente['ip']
            puerto_cliente = info_cliente['puerto']
            uri_cliente = info_cliente['uri']
            self.logger.warning(f"informacion Cliente Recibida:{info_cliente}")
            self.dispacher.manejar_llamada(
                "comunicacion", # nombre_servicio
                "suscribir_cliente", # nombre_metodo
                nickname, nombre_logico, ip_cliente, puerto_cliente, uri_cliente# args
            )
            self.logger.info(f"Jugador {nickname} suscripto como nuevo.")
            

            # obtener info sala
            nicknames_jugadores: list[str] = self.dispacher.manejar_llamada(
                "comunicacion",  # nombre_servicio
                "listado_nicknames",  # nombre_metodo
            )

            info_sala: dict = self.Partida.get_info_sala()
            info_sala['jugadores'] = nicknames_jugadores

            self.Jugadores[nickname] = False

            json_nuevo_jugador = SerializeHelper.serializar(exito=True, msg="nuevo_jugador_sala", datos={
                'nickname': nickname
            })
            self.dispacher.manejar_llamada(
                "comunicacion",  # nombre_servicio
                "broadcast_a_clientes",  # nombre_metodo
                 json_nuevo_jugador#args
            )
            # retorna info de sala a quien se unió
            return SerializeHelper.respuesta(
                exito=True,
                msg="Se ha unido a la sala exitosamente",
                datos=info_sala
            )
        except Exception as e:  # Catches any other exception
            self.logger.error(f"Ocurrio un error al unirse a la sala: {e}")


    def salir_de_sala(self, nickname: str):
        pass
        """
        result = self.publisher.desuscribirJugador(nickname)
        if result is None:
            self.gui.show_error("[salir_de_sala] Jugador {nickname} no existe en la sala")
            return None
        """
    
    def _verificar_jugadores_suficientes(self) -> bool:
        return len(list(filter(bool, self.Jugadores.values()))) >= self.jugadores_min

    def ver_jugadores_partida(self):
        return self.Jugadores
    
    def obtener_jugadores_en_partida(self) -> list[str]:
        nicknames_jugadores_conectados: list[str] = self.dispacher.manejar_llamada("comunicacion", "listado_nicknames")
        return nicknames_jugadores_conectados

    def get_sala(self):
        return self.Partida.get_info_sala()
    
    def get_info_ronda_actual(self):
        return self.Partida.get_info_ronda()
    
    def obtener_jugadores_en_partida(self) -> list[str]:
        nicknames_jugadores_conectados: list[str] = self.dispacher.manejar_llamada("comunicacion", "listado_nicknames")
        return nicknames_jugadores_conectados

    def recibir_stop(self):
        with self.lock_confirmacion:
            if self.Partida.ronda_actual.get_estado_ronda():
                return  # Ya se finalizó la ronda, ignora llamadas extra
            self.Partida.ronda_actual.set_estado_ronda(True)
            threading.Thread(target=self.enviar_respuestas_ronda, daemon=True).start()


    def confirmar_jugador(self, nickname: str):
        # lock -> evitar condicion de carrera
        with self.lock_confirmacion:
            if nickname not in self.Jugadores:
                self.logger.warning(f"[confirmar_jugador] Jugador {nickname} no existe en la sala")
                return SerializeHelper.respuesta(
                    exito=False,
                    msg=f"Jugador {nickname} no existe en la sala"
                )

            if self.Jugadores[nickname] is True:
                self.logger.warning(f"[confirmar_jugador] Jugador {nickname} ya estaba confirmado")
                return SerializeHelper.respuesta(
                    exito=False,
                    msg=f"Jugador {nickname} ya estaba confirmado"
                )

            # Confirmar jugador
            self.Jugadores[nickname] = True
            self.logger.info(f"[confirmar_jugador] Jugador {nickname} confirmado")
            #---------------------------------------------------------------------------------------------------------------
            #ACA TENGO QUE AGREGAR EL NUEVO CLIENTE A LA BD?
            #Acá traigo el cliente confirmado para poder obtener sus datos de conexión
            cliente_confirmado: ClienteConectado = self.dispacher.manejar_llamada(
            "comunicacion", # nombre_servicio
            "getDatosCliente", # nombre_metodo
            nickname # args
            ) 
            # Creo cliente_conectado, que es el diccionario para agregar en la BDD, dentro de los clientes conectados.
            cliente_conectado = {
                "nickname": cliente_confirmado.nickname,
                "ip": cliente_confirmado.socket.host,
                "puerto": cliente_confirmado.socket.puerto,
                "uri": str(cliente_confirmado.uri_cliente_conectado),
                "puntaje_total": 0  # Inicializar puntaje en 0
            }

            """ if self.db.agregar_jugador(cliente_conectado) > 0: #agrego el jugador y devuelvo un log confirmando
                self.logger.info(f"[DB] Se agrego al jugador {cliente_conectado['nickname']} a la lista de clientes_conectados")
            else: 
                self.logger.warning(f"[DB] El jugador {cliente_conectado['nickname']} no ha sido cargado en la DB")   """       
            
            new_cliente_conectado = self.dispacher.manejar_llamada("db","agregar_jugador", cliente_conectado)
            if new_cliente_conectado > 0: #agrego el jugador y devuelvo un log confirmando
                self.logger.info(f"[DB] Se agrego al jugador {cliente_conectado['nickname']} a la lista de clientes_conectados")
                """
                Actualizacion a replicas 
                json = SerializeHelper.serializar(exito=True, msg="confirmar_jugador", datos=cliente_conectado)
                self.dispacher.manejar_llamada("nodo_ppal", "broadcast_a_nodos", json)
                """
            else: 
                self.logger.warning(f"El jugador {cliente_conectado['nickname']} no ha sido cargado en la DB")            
            #---------------------------------------------------------------------------------------------------------------

            # Verificar si se puede iniciar la partida
            jugadores_suficientes = self._verificar_jugadores_suficientes()
            self.logger.warning(f"jugadores_suficientes: {jugadores_suficientes}")
            if jugadores_suficientes:
                # Notificacion mediante Sockets
                hilo = threading.Thread(target=self.iniciar_partida, daemon=True)
                hilo.start()

                return SerializeHelper.respuesta(
                    exito=True,
                    msg=f"{nickname} confirmado correctamente. ¡La partida comienza!",
                )
            else:
                return SerializeHelper.respuesta(
                    exito=True,
                    msg=f"{nickname} confirmado correctamente. Esperando a los demás...",
                )

            #Opcional, agregar mensaje por socket. por jugador, aunque lo mejor es dejarlo
            # para cuando inicie la ronda a todos

    def eliminar_jugador(self,nickname):
        #Si existe la partida, elimina el jugador
        #Esta logica puede modificarse para aceptar reconexion si se implementa la linea 339 en solicitar_acceso
        if self.Partida:
            #self.Partida.eliminar_jugador_partida(nickname)
            # Verificar si el jugador existe antes de eliminarlo
            if nickname in self.Jugadores:
                self.Jugadores.pop(nickname) #si se permite reconexion, esta linea se borra, pero
                self.logger.info(f"Jugador {nickname} eliminado de la partida")
            else:
                self.logger.warning(f"Intento de eliminar jugador {nickname} que no existe en la partida")

#NOTA: en vez de eliminar el jugador de la lista de partida, conviene borrarlo solo de la lista local, para evitar tener que cargar todos los datos de nuevo