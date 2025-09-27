import threading
from threading import Lock, Thread
import time
from collections import defaultdict, Counter

import Pyro5.api

from Servidor.Comunicacion.Dispacher import Dispatcher
from Servidor.Dominio.Jugador import Jugador
from Servidor.Dominio.Partida import Partida
from Servidor.Utils.ConsoleLogger import ConsoleLogger
from Servidor.Utils.SerializeHelper import SerializeHelper

@Pyro5.api.expose
class ServicioJuego:
    def __init__(self, dispacher: Dispatcher,logger=ConsoleLogger(name="ServicioJuego", level="INFO")):
        self.dispacher = dispacher
        self.partida = Partida()
        self.logger = logger # cambiar si se necesita 'DEBUG'
        self.jugadores_min = 2 # pasar por constructor?
        self.logger.info("Servicio Juego inicializado")
        self.Jugadores = {}  # Pasar a OBJETO JUGADOR
        self.lock_confirmacion = Lock()

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
        return self.partida.get_info_sala()

    def obtener_info_sala(self) -> dict:
        return self.partida.get_info_sala()

    def iniciar_partida(self):
        # Inicia la 1ra Ronda
        self.partida.iniciar_nueva_ronda() # Ronda 1

        jugadores: list[Jugador] = [Jugador(nick) for nick in self.Jugadores.keys()]
        self.partida.cargar_jugadores_partida(jugadores)

        info_ronda: dict = self.partida.get_info_ronda()
        json = SerializeHelper.serializar(exito=True, msg="nueva_ronda", datos=info_ronda)
        self.dispacher.manejar_llamada(
            "comunicacion",
            "broadcast",
            json)

    def enviar_respuestas_ronda(self):
        # Aviso a Clientes que termino la ronda
        json = SerializeHelper.serializar(exito=True, msg="fin_ronda")
        self.dispacher.manejar_llamada(
            "comunicacion",
            "broadcast",
            json)
        
        json = SerializeHelper.serializar(exito=True, msg="inicio_votacion")
        self.dispacher.manejar_llamada(
            "comunicacion",
            "broadcast",
            json)

        # obtenerRespuesMemoriaClientes
        respuestas_clientes: dict = self.dispacher.manejar_llamada(
            "comunicacion",
            "respuestas_memoria_clientes_ronda")

        self.partida.ronda_actual.set_respuestas_ronda(respuestas_clientes)
        
        info_completa_votacion = {
            'nro_ronda' : self.partida.nro_ronda_actual,
            'total_rondas':self.partida.rondas_maximas,
            'letra_ronda': self.partida.ronda_actual.letra_ronda,
            'respuestas_clientes': respuestas_clientes
        }
        
        self.dispacher.manejar_llamada("comunicacion",
        "enviar_datos_para_votacion",
        info_completa_votacion)

        """Se ejecuta el timer en un hilo separado para no bloquear la llamada remota del cliente que hace STOP"""
        hilo_timer = threading.Thread(target=self.timer_votacion, daemon=True)
        hilo_timer.start()


    def timer_votacion(self):
        tiempos = [30, 20, 10]
        for t in tiempos:
            mensaje = SerializeHelper.serializar(exito=True, msg="aviso_tiempo_votacion", datos=f"Te quedan {t} segundos para votar")
            self.dispacher.manejar_llamada("comunicacion", "broadcast", mensaje)
            time.sleep(10)  # Espera 10 segundos entre avisos

        #se quedaría 

        hilo_pedir_votos = threading.Thread(target=self.obtener_votos_jugadores, daemon=True)
        hilo_pedir_votos.start()
        

        
    def evaluar_ultima_ronda(self):
        if self.partida.nro_ronda_actual == self.partida.rondas_maximas:
            self.finalizar_partida() #manda señal para ir a resultado
        else:
            self.partida.iniciar_nueva_ronda()
            info_ronda = self.partida.get_info_ronda()
            json = SerializeHelper.serializar(exito=True, msg="nueva_ronda", datos=info_ronda) #Cambie a la vista Ronda nueva
            self.dispacher.manejar_llamada(
                "comunicacion",  # nombre_servicio
                "broadcast",  # nombre_metodo
                    json#args
            )


    def obtener_votos_jugadores(self):
        votos = self.dispacher.manejar_llamada("comunicacion", #Recolectar los votos de la vista
        "recolectar_votos")
        self.procesar_votos_y_asignar_puntaje(votos)

    """
    def procesar_votos_y_asignar_puntaje(self, votos):
        respuestas_clientes = self.partida.ronda_actual.get_respuestas_ronda()
        from collections import defaultdict

        conteo_respuestas = defaultdict(lambda: defaultdict(int))

        validez = defaultdict(dict)
        for jugador, info in respuestas_clientes.items():
            
            if not info.get("respuestas", {}):   # se evalúa True si está vacío
                self.logger.warning(f"No hay respuestas registradas para jugador {jugador}")
                continue  # saltar al siguiente jugador
           
            for categoria, respuesta in info["respuestas"].items():
                true_count = 0
                false_count = 0
                for ronda, votos_jugadores in votos.items():
                    if jugador in votos_jugadores and categoria in votos_jugadores[jugador]:
                        if votos_jugadores[jugador][categoria]:
                            true_count += 1
                        else:
                            false_count += 1
                
                validez[jugador][categoria] = (true_count > false_count)
                
                # Solo cuenta la respuesta si es válida y no vacía
                if respuesta and validez[jugador][categoria]:
                    conteo_respuestas[categoria][respuesta] += 1

        puntajes = {}
        for jugador, info in respuestas_clientes.items():
            puntajes[jugador] = {}

            if not info.get("respuestas", {}):   # se evalúa True si está vacío
                self.logger.warning(f"No hay respuestas registradas para jugador {jugador}")
                continue  # saltar al siguiente jugador

            for categoria, respuesta in info["respuestas"].items():
                if not respuesta or not validez[jugador][categoria]:
                    puntaje = 0
                else:
                    repeticiones = conteo_respuestas[categoria][respuesta]
                    if repeticiones == 1:
                        puntaje = 10  # Respuesta única
                    else:
                        puntaje = 5   # Respuesta repetida
                puntajes[jugador][categoria] = puntaje
                print(f"[DEBUG] {jugador} - {categoria}: '{respuesta}' | T:{true_count} F:{false_count} válida: {validez[jugador][categoria]}, repeticiones: {conteo_respuestas[categoria][respuesta]} => {puntaje} puntos")

        totales = {jugador: sum(categorias.values()) for jugador, categorias in puntajes.items()}

        # Posible KeyError? en 1 ejecucion me salio, el resto normal
        #self.logger.error(f"jugadores dict totales: {totales.keys()}")
        #self.logger.error(f"jugadores en self.partida.jugadores: {self.partida.jugadores}")

        for jugador in self.partida.jugadores:
            if jugador.nickname in totales:
                jugador.sumar_puntaje(totales[jugador.nickname])
            print(f"El puntaje del jugador {jugador.nickname} es {totales[jugador.nickname]}")

        self.evaluar_ultima_ronda()
    """

    def procesar_votos_y_asignar_puntaje(self, votos):
        from collections import defaultdict

        respuestas_clientes = self.partida.ronda_actual.get_respuestas_ronda()
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

        for jugador in self.partida.jugadores:
            total = totales.get(jugador.nickname, 0)  # evita KeyError
            jugador.sumar_puntaje(total)
            self.logger.info(f"El puntaje del jugador {jugador.nickname} es {total}")

        self.evaluar_ultima_ronda()



    def finalizar_partida(self):
        """Notifica el fin de la partida y envía los datos finales"""

        puntajes_totales, ganador = self.partida.calcular_puntos_partida()

        resultados_partida = {
            'jugadores' : list(self.Jugadores.keys()),
            'puntajes_totales': puntajes_totales,
            'ganador':ganador
        }

        json = SerializeHelper.serializar(exito=True, msg="fin_partida", datos=resultados_partida)
        self.dispacher.manejar_llamada(
            "comunicacion",  # nombre_servicio
            "broadcast",  # nombre_metodo
                json#args
        )


    # PENDIENTE - Manejar intentos de unirse o acceso en otros estados de la partida
    def solicitar_acceso(self):
        hay_lugar: bool = self.dispacher.manejar_llamada(
            "comunicacion", # nombre_servicio
            "hay_lugar_disponible", # nombre_metodo
            self.jugadores_min # args
        )

        if not hay_lugar:
            return SerializeHelper.respuesta(
                exito=False,
                msg="La sala está llena, no puede unirse."
            )

        # hay lugar
        return SerializeHelper.respuesta(
            exito=True,
            msg="Hay lugar disponible, puede unirse."
        )


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

    def unirse_a_sala(self, info_cliente: dict):
        """
        1. Verificar si existe ya jugador en sala ???
        2. Suscribir / Registrar Jugador
        3. Conectarse al socket del Cliente (se hace al suscribir cliente)
        4. Notificar entrada de nuevo a todos los jugadores (broadcast)
        5. Obtener info Sala
        6. Retornar info Sala via Pyro
        """
        try:
            nickname = info_cliente['nickname']
            nombre_logico = info_cliente['nombre_logico']
            ip_cliente = info_cliente['ip']
            puerto_cliente = info_cliente['puerto']
            uri_cliente = info_cliente['uri']
            self.dispacher.manejar_llamada(
                "comunicacion",  # nombre_servicio
                "suscribir_cliente",  # nombre_metodo
                nickname, nombre_logico, ip_cliente, puerto_cliente, uri_cliente  # args
            )

            # obtener info sala
            nicknames_jugadores: list[str] = self.dispacher.manejar_llamada(
                "comunicacion",  # nombre_servicio
                "listado_nicknames",  # nombre_metodo
            )

            info_sala: dict = self.partida.get_info_sala()
            info_sala['jugadores'] = nicknames_jugadores

            self.Jugadores[nickname] = False

            json_nuevo_jugador = SerializeHelper.serializar(exito=True, msg="nuevo_jugador_sala", datos={
                'nickname': nickname
            })
            self.dispacher.manejar_llamada(
                "comunicacion",  # nombre_servicio
                "broadcast",  # nombre_metodo
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
        return self.partida.get_info_sala()
    
    def get_info_ronda_actual(self):
        return self.partida.get_info_ronda()
    
    def obtener_jugadores_en_partida(self) -> list[str]:
        nicknames_jugadores_conectados: list[str] = self.dispacher.manejar_llamada("comunicacion", "listado_nicknames")
        return nicknames_jugadores_conectados

    def recibir_stop(self):
        with self.lock_confirmacion:
            if self.partida.ronda_actual.get_estado_ronda():
                return  # Ya se finalizó la ronda, ignora llamadas extra
            self.partida.ronda_actual.set_estado_ronda(True)
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

            # Verificar si se puede iniciar la partida
            jugadores_suficientes = self._verificar_jugadores_suficientes()
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
        self.partida.eliminar_jugador_partida(nickname)
        self.Jugadores.pop(nickname)
