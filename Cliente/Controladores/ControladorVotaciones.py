from Cliente.A_Vistas.VistaVotaciones import VistaVotaciones
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QMetaObject
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
        self.signals.actualizar_vista_signal.connect(self.vista.reiniciar_labels,Qt.ConnectionType.QueuedConnection)
        self.signals.actualizar_vista_signal.connect(self._actualizar_vista_votaciones,Qt.ConnectionType.QueuedConnection)
        self.signals.actualizar_mensaje_timer_signal.connect(self.vista.set_mensaje_votacion, Qt.ConnectionType.QueuedConnection)

        """
        La línea de abajo sirve para saber en qué hilo estás, sirvió para probar que las señales se estaban enviando desde un hilo pyro (que tiene origen en
        ServicioComunicacion) hacia el hilo de la gui.
        print(f"[DEBUG] ControladorVotaciones creado en hilo: {threading.current_thread().name}")
        """

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion

    def mostrar_info_votaciones(self, respuestas_clientes):
        self.signals.actualizar_vista_signal.emit(respuestas_clientes)

    def _actualizar_vista_votaciones(self, respuestas_clientes: dict):
        letra = respuestas_clientes.get('letra_ronda', 'A')
        nro_ronda = respuestas_clientes.get('nro_ronda', 1)
        total_rondas = respuestas_clientes.get('total_rondas', 3)
    
        # Actualiza la cabecera de la vista
        self.vista.set_ronda_y_letra(nro_ronda, total_rondas, letra)

        # Transforma las respuestas al formato esperado por la vista
        respuestas_por_categoria = {}
        # 'NICKNAME' es la clave del diccionario
        for nickname, info in respuestas_clientes['respuestas_clientes'].items():
            for categoria, respuesta in info['respuestas'].items():
                clave = f"{categoria} con {letra}"
                if clave not in respuestas_por_categoria:
                    respuestas_por_categoria[clave] = []
                respuestas_por_categoria[clave].append((nickname, respuesta))
        self.vista.agregar_respuestas_para_votar(respuestas_por_categoria)
    
    def actualizar_mensaje_timer(self, mensaje):
        self.signals.actualizar_mensaje_timer_signal.emit(mensaje)

    def enviar_votos(self):
        return self.vista.obtener_votos()

        
