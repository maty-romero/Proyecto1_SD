"""Flujo:
    -Se crean las vistas, y se agregan al stack
    -El stack es la referencia para todas las vistas, permite cambiarlas a discrecion a medida que se necesite
    - Se cambia entre ellas usando setCurrentIndex() o setCurrentWidget() 

    -update: ya no se cambia con setCurrentIndex, sino con un metodo unico que recibe el nombre de la vista a mostrar
    -esto permite un mejor desacoplamiento, ya que las vistas no necesitan conocer los indices

    - Por una cuestion de simplicidad, cada controlador recibe el controlador de navegacion
    - Va a haber acoplamiento, dado que este controlador conocera a todos los demas
    """

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
                 vistaSala, vistaRonda, controlador_votaciones, vistaVotaciones):
        self.main_window = main_window

        # Guardar referencias a controladores
        self.controlador_nickname = controlador_nickname
        self.controlador_sala = controlador_sala
        self.controlador_ronda = controlador_ronda
        self.controlador_votaciones = controlador_votaciones

        # Guardar referencias a vistas
        self.vistaNickname = vistaNickname
        self.vistaSala = vistaSala
        self.vistaRonda = vistaRonda
        self.vistaVotaciones = vistaVotaciones

        # Agregar vistas al stack
        self.vistaNickname_Index = self.main_window.stack.addWidget(self.vistaNickname)
        self.vistaSala_Index = self.main_window.stack.addWidget(self.vistaSala)
        self.vistaRonda_Index = self.main_window.stack.addWidget(self.vistaRonda)
        self.vistaVotaciones_Index = self.main_window.stack.addWidget(self.vistaVotaciones)

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
            self.controlador_votaciones.mostrar_info_votaciones()  # Lo mismo que pasó con sala
            self.main_window.stack.setCurrentIndex(self.vistaVotaciones_Index)
        elif eleccion == "resultados":
            pass
            #self.main_window.stack.setCurrentIndex(self.vistaResultados_Index)
        else:
            raise ValueError(f"Vista '{eleccion}' no encontrada")
    
    def obtener_respuestas_ronda(self):
        # Llama al método del controlador de ronda
        return self.controlador_ronda.obtener_respuestas()