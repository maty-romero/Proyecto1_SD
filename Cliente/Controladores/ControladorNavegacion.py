"""Flujo:
    -Se crean las vistas, y se agregan al stack
    -El stack es la referencia para todas las vistas, permite cambiarlas a discrecion a medida que se necesite
    - Se cambia entre ellas usando setCurrentIndex() o setCurrentWidget() 

    -update: ya no se cambia con setCurrentIndex, sino con un metodo unico que recibe el nombre de la vista a mostrar
    -esto permite un mejor desacoplamiento, ya que las vistas no necesitan conocer los indices

    - Por una cuestion de simplicidad, cada controlador recibe el controlador de navegacion
    - Va a haber acoplamiento, dado que este controlador conocera a todos los demas
    """

from PyQt6.QtCore import QTimer
from Cliente.A_Vistas.VistaMensajeTransitorio import VistaMensajeTransitorio
from Cliente.A_Vistas.VistaNickname import VistaNickname
from Cliente.A_Vistas.VistaSala import VistaSala
from Cliente.A_Vistas.VistaRonda import VistaRonda
#from Cliente.A_Vistas.ResultadosView import VistaResultados

from Cliente.Controladores.ControladorNickname import ControladorNickName
from Cliente.Controladores.ControladorRonda import ControladorRonda
from Cliente.Controladores.ControladorSala import ControladorSala

class ControladorNavegacion:
    def __init__(self, main_window,controlador_nickname,
                 controlador_sala,controlador_ronda, vistaNickname,
                 vistaSala, vistaRonda, controlador_votaciones, vistaVotaciones,controlador_resultados, 
                 vistaResultados):
        
        self.main_window = main_window

        # Guardar referencias a controladores
        self.controlador_nickname = controlador_nickname
        self.controlador_sala = controlador_sala
        self.controlador_ronda = controlador_ronda
        self.controlador_votaciones = controlador_votaciones
        self.controlador_resultados = controlador_resultados
        # self.controlador_mensaje No hace falta controlador, control de transiciones - controlador nav 

        # Guardar referencias a vistas
        self.vistaNickname = vistaNickname
        self.vistaSala = vistaSala
        self.vistaRonda = vistaRonda
        self.vistaVotaciones = vistaVotaciones
        self.vistaResultados = vistaResultados
        #self.vistaMensaje = VistaMensajeTransitorio()

        # Agregar vistas al stack
        self.vistaNickname_Index = self.main_window.stack.addWidget(self.vistaNickname)
        self.vistaSala_Index = self.main_window.stack.addWidget(self.vistaSala)
        self.vistaRonda_Index = self.main_window.stack.addWidget(self.vistaRonda)
        self.vistaVotaciones_Index = self.main_window.stack.addWidget(self.vistaVotaciones)
        self.vistaResultados_Index = self.main_window.stack.addWidget(self.vistaResultados)
        #elf.vistaMensaje_Index = self.main_window.stack.addWidget(self.vistaMensaje)

    # --- Métodos de navegación ---
      #  Cada método cambia la vista actual del stack a la vista correspondiente, metodo unico para favorecer desacoplamiento
    
    def mostrar(self, eleccion: str):
        if eleccion == "nickname":
            self.main_window.stack.setCurrentIndex(self.vistaNickname_Index)
        elif eleccion == "sala":
            self.controlador_sala.mostrar_info_sala()  # Esto es para "actualizar" la vista de sala con los datos reales
            self.main_window.stack.setCurrentIndex(self.vistaSala_Index)
        elif eleccion == "ronda":
            self.controlador_ronda.mostrar_info_ronda() #Lo mismo que pasó con sala
            self.main_window.stack.setCurrentIndex(self.vistaRonda_Index)
        elif eleccion == "votaciones":   
            self.controlador_votaciones.vista.reiniciar_labels()  # Limpiar vista antes de mostrarla
            self.main_window.stack.setCurrentIndex(self.vistaVotaciones_Index)
        elif eleccion == "resultados":
            self.main_window.stack.setCurrentIndex(self.vistaResultados_Index)
        elif eleccion == "mensaje": 
            self.main_window.stack.setCurrentIndex(self.vistaMensaje_Index)
        else:
            raise ValueError(f"Vista '{eleccion}' no encontrada")
    
    def obtener_respuestas_ronda(self):
        # Llama al método del controlador de ronda
        return self.controlador_ronda.obtener_respuestas()
    
    # def mostrar_mensaje_transitorio(self, texto: str):
    #     self.vistaMensaje.setMensaje(texto)
    #     self.main_window.stack.setCurrentIndex(self.vistaMensajeTransitorio_Index)

    def mostrar_mensaje_reconexion(self, cliente, callback_reconexion, callback_fallo):
        """
        Muestra la vista de mensaje transitorio con opción de reconectar por 10 segundos.
        callback_reconexion: función a llamar si el usuario elige reconectar
        callback_fallo: función a llamar si elige no reconectar o se acaba el tiempo
        """
        self.vistaMensaje = VistaMensajeTransitorio()
        self.vistaMensaje.setMensaje("¿Desea reconectarse? (10 segundos para decidir)")
        self.vistaMensajeTransitorio_Index = self.main_window.stack.addWidget(self.vistaMensaje)
        self.main_window.stack.setCurrentIndex(self.vistaMensajeTransitorio_Index)

        self._timer_reconexion = QTimer()
        self._timer_reconexion.setSingleShot(True)
        self._timer_reconexion.timeout.connect(lambda: self._on_reconexion_fallo(callback_fallo))
        self._timer_reconexion.start(10000)  # 10 segundos

        self.vistaMensaje.boton_si.clicked.connect(lambda: self._on_reconexion_si(callback_reconexion, cliente))
        self.vistaMensaje.boton_no.clicked.connect(lambda: self._on_reconexion_fallo(callback_fallo))

    def _on_reconexion_si(self, callback_reconexion, cliente):
        self._timer_reconexion.stop()
        dict_cliente_reconectado = {
            'nickname': cliente.nickname,
            'nombre_logico': cliente.nombre_logico,
            'ip': cliente.ip_cliente,
            'puerto': cliente.puerto_cliente,
            'uri': cliente.uri_cliente
        }
        callback_reconexion(dict_cliente_reconectado)

    def _on_reconexion_fallo(self, callback_fallo):
        if hasattr(self, '_timer_reconexion'):
            self._timer_reconexion.stop()
        self.vistaMensaje.setMensaje("No se pudo reconectar. Cerrando la aplicación.")
        if callback_fallo:
            callback_fallo()

    """
    def mostrar_mensaje_transitorio_temporal(self, texto: str, siguiente_vista: str, duracion_ms=3000):
        self.mostrar_mensaje_transitorio(texto)
        QtCore.QTimer.singleShot(duracion_ms, lambda: self.mostrar(siguiente_vista))

    """