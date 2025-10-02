from Cliente.A_Vistas.VistaVotaciones import VistaVotaciones
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QMetaObject

from Utils.ConsoleLogger import ConsoleLogger
class VotacionesSignals(QObject):
    """Clase que hereda de QObject para poder utilizar señales pyqtSignal"""
    actualizar_vista_signal = pyqtSignal(dict) #Esta señal sirve para comunicarse desde un hilo secundario al hilo de la gui, de lo contrario no se puede modificar la gui
    actualizar_mensaje_timer_signal = pyqtSignal(str) #Señal para actualizar el mensaje del timer de forma thread-safe
    def __init__(self):
        super().__init__()

class ControladorVotaciones:
    def __init__(self, vista: 'VistaVotaciones', gestor_cliente):
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente = gestor_cliente
        self.signals = VotacionesSignals()
        #self.signals.actualizar_vista_signal.connect(self.vista.reiniciar_labels,Qt.ConnectionType.QueuedConnection)
        self.signals.actualizar_vista_signal.connect(self._actualizar_vista_votaciones,Qt.ConnectionType.QueuedConnection)
        self.signals.actualizar_mensaje_timer_signal.connect(self.vista.set_mensaje_votacion, Qt.ConnectionType.QueuedConnection)

        self.logger = ConsoleLogger(name="ControladorVotaciones", level="INFO")


        """
        La línea de abajo sirve para saber en qué hilo estás, sirvió para probar que las señales se estaban enviando desde un hilo pyro (que tiene origen en
        ServicioComunicacion) hacia el hilo de la gui.
        print(f"[DEBUG] ControladorVotaciones creado en hilo: {threading.current_thread().name}")
        """

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion

    def mostrar_info_votaciones(self, respuestas_clientes):
        self.signals.actualizar_vista_signal.emit(respuestas_clientes)

    # def _actualizar_vista_votaciones(self, respuestas_clientes: dict):
    #     letra = respuestas_clientes.get('letra_ronda', 'A')
    #     nro_ronda = respuestas_clientes.get('nro_ronda', 1)
    #     total_rondas = respuestas_clientes.get('total_rondas', 3)
    
    #     # Actualiza la cabecera de la vista
    #     self.vista.set_ronda_y_letra(nro_ronda, total_rondas, letra)

    #     # Transforma las respuestas al formato esperado por la vista
    #     respuestas_por_categoria = {}
    #     # 'NICKNAME' es la clave del diccionario
    #     for nickname, info in respuestas_clientes['respuestas_clientes'].items():

    #         if not info.get("respuestas", {}):   # se evalúa True si está vacío
    #             self.logger.warning(f"No hay respuestas registradas para jugador {nickname}")
    #             continue  # saltar al siguiente jugador

    #         for categoria, respuesta in info['respuestas'].items():
    #             clave = f"{categoria} con {letra}"
    #             if clave not in respuestas_por_categoria:
    #                 respuestas_por_categoria[clave] = []
    #             respuestas_por_categoria[clave].append((nickname, respuesta))
    #     self.vista.agregar_respuestas_para_votar(respuestas_por_categoria)

    def _actualizar_vista_votaciones(self, respuestas_clientes: dict):
        letra = respuestas_clientes.get('letra_ronda', 'A')
        nro_ronda = respuestas_clientes.get('nro_ronda', 1)
        total_rondas = respuestas_clientes.get('total_rondas', 3)

        # Actualiza la cabecera de la vista
        self.vista.set_ronda_y_letra(nro_ronda, total_rondas, letra)

        # Transforma las respuestas al formato esperado por la vista
        respuestas_por_categoria = {}
        
        # Iterar sobre cada jugador y sus respuestas
        for nickname, info in respuestas_clientes['respuestas_clientes'].items():
            
            # DEBUG: Ver datos de cada jugador
            self.logger.info(f"DEBUG - Procesando jugador '{nickname}': {info}")
            self.logger.info(f"DEBUG - Tipo de info: {type(info)}")
            
            if not info:   # Verificar si info está vacío
                self.logger.warning(f"No hay respuestas registradas para jugador {nickname}")
                continue  # saltar al siguiente jugador

            # MANEJO DE AMBAS ESTRUCTURAS
            respuestas = None
            
            # Verificar si tiene la estructura antigua: {"respuestas": {...}}
            if isinstance(info, dict) and "respuestas" in info:
                # ESTRUCTURA ANTIGUA: {"respuestas": {"Nombres": "valor", ...}}
                respuestas = info["respuestas"]
                self.logger.info(f"DEBUG - Usando estructura ANTIGUA para {nickname}")
                
            elif isinstance(info, dict):
                # ESTRUCTURA NUEVA: {"Nombres": "valor", "Animales": "valor", ...}
                respuestas = info
                self.logger.info(f"DEBUG - Usando estructura NUEVA para {nickname}")
                
            else:
                self.logger.error(f"ERROR - Estructura no reconocida para jugador {nickname}: {type(info)}")
                continue

            # Verificar que tenemos respuestas válidas
            if not respuestas:
                self.logger.warning(f"No hay respuestas válidas para jugador {nickname}")
                continue

            # Procesar las respuestas (independiente de la estructura)
            for categoria, respuesta in respuestas.items():
                self.logger.info(f"DEBUG - Categoría: '{categoria}', Respuesta: '{respuesta}' (tipo: {type(respuesta)})")
                
                # Verificar que la respuesta es un string
                if not isinstance(respuesta, str):
                    self.logger.warning(f"Respuesta no es string, convirtiendo: {respuesta}")
                    respuesta = str(respuesta)
                
                # Crear la clave con formato "Categoria con Letra"
                clave = f"{categoria} con {letra}"
                
                # Inicializar la lista si no existe
                if clave not in respuestas_por_categoria:
                    respuestas_por_categoria[clave] = []
                
                # Agregar la tupla (nickname, respuesta) a la categoría
                respuestas_por_categoria[clave].append((nickname, respuesta))
        
        # DEBUG: Ver el resultado final
        self.logger.info(f"DEBUG - Resultado final para la vista: {respuestas_por_categoria}")
        
        # Enviar los datos transformados a la vista
        self.vista.agregar_respuestas_para_votar(respuestas_por_categoria)

    
    # def actualizar_mensaje_timer(self, mensaje):
    #     self.signals.actualizar_mensaje_timer_signal.emit(mensaje)

    def actualizar_mensaje_timer(self, datos):
        """Actualizar mensaje del timer de forma thread-safe"""
        try:
            # MANEJAR AMBOS FORMATOS: dict y string
            if isinstance(datos, dict):
                # Formato nuevo: {'tiempo_restante': X}
                tiempo_restante = datos.get('tiempo_restante', 0)
                mensaje = f"Te quedan {tiempo_restante} segundos para votar"
            else:
                # Formato actual: "Te quedan X segundos para votar" (string)
                mensaje = str(datos)
            
            # Enviar mensaje a la vista
            self.signals.actualizar_mensaje_timer_signal.emit(mensaje)
            
        except Exception as e:
            self.logger.error(f"Error actualizando timer: {e}")
            # Fallback: enviar mensaje genérico
            self.signals.actualizar_mensaje_timer_signal.emit("Votación en curso...")

    def mostrar_tiempo_agotado(self, mensaje):
        """Muestra mensaje cuando el tiempo de votación se agota"""
        try:
            # Extraer mensaje si viene en formato dict
            if isinstance(mensaje, dict):
                texto_mensaje = mensaje.get('mensaje', '¡Tiempo agotado!')
            else:
                texto_mensaje = str(mensaje)
                
            # Actualizar la vista con el mensaje final
            self.signals.actualizar_mensaje_timer_signal.emit(texto_mensaje)
            
            self.logger.info(f"Tiempo de votación agotado: {texto_mensaje}")
            
        except Exception as e:
            self.logger.error(f"Error mostrando tiempo agotado: {e}")
            # Fallback
            self.signals.actualizar_mensaje_timer_signal.emit("¡Tiempo agotado!")


    def enviar_votos(self):
        votos = self.vista.obtener_votos()
        print(f"VOTOS QUE MANDÉ: {votos}")
        return votos

        
