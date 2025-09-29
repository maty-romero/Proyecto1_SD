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
import threading

from Cliente.Controladores.ControladorNickname import ControladorNickName
from Cliente.Controladores.ControladorRonda import ControladorRonda
from Cliente.Controladores.ControladorSala import ControladorSala

class ControladorNavegacion:
    def __init__(self, main_window,controlador_nickname,
                 controlador_sala,controlador_ronda, vistaNickname,
                 vistaSala, vistaRonda, controlador_votaciones, vistaVotaciones,controlador_resultados, 
                 vistaResultados,  controlador_mensaje, vistaMensaje):
        
        self.main_window = main_window

        # Guardar referencias a controladores
        self.controlador_nickname = controlador_nickname
        self.controlador_sala = controlador_sala
        self.controlador_ronda = controlador_ronda
        self.controlador_votaciones = controlador_votaciones
        self.controlador_resultados = controlador_resultados
        # self.controlador_mensaje No hace falta controlador, control de transiciones - controlador nav
        self.controlador_mensaje = controlador_mensaje

        # Guardar referencias a vistas
        self.vistaNickname = vistaNickname
        self.vistaSala = vistaSala
        self.vistaRonda = vistaRonda
        self.vistaVotaciones = vistaVotaciones
        self.vistaResultados = vistaResultados
        self.vistaMensaje = vistaMensaje

        # Agregar vistas al stack
        self.vistaNickname_Index = self.main_window.stack.addWidget(self.vistaNickname)
        self.vistaSala_Index = self.main_window.stack.addWidget(self.vistaSala)
        self.vistaRonda_Index = self.main_window.stack.addWidget(self.vistaRonda)
        self.vistaVotaciones_Index = self.main_window.stack.addWidget(self.vistaVotaciones)
        self.vistaResultados_Index = self.main_window.stack.addWidget(self.vistaResultados)
        self.vistaMensaje_Index = self.main_window.stack.addWidget(self.vistaMensaje)

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
            print(f"4. [DEBUG] Desde ControladorNvegacion - se selecciona la vista del stack mainWindow - en hilo: {threading.current_thread().name}")
            self.main_window.show()
            self.main_window.stack.setCurrentIndex(self.vistaMensaje_Index)
        else:
            raise ValueError(f"Vista '{eleccion}' no encontrada")
    
    def obtener_respuestas_ronda(self):
        # Llama al método del controlador de ronda
        return self.controlador_ronda.obtener_respuestas()
    
    # def mostrar_mensaje_transitorio(self, texto: str):
    #     self.vistaMensaje.setMensaje(texto)
    #     self.main_window.stack.setCurrentIndex(self.vistaMensajeTransitorio_Index)

    """
    def mostrar_mensaje_transitorio_temporal(self, texto: str, siguiente_vista: str, duracion_ms=3000):
        self.mostrar_mensaje_transitorio(texto)
        QtCore.QTimer.singleShot(duracion_ms, lambda: self.mostrar(siguiente_vista))

    """