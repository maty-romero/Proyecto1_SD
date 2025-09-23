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
    def __init__(self, main_window,controlador_nickname,controlador_sala,controlador_ronda,vistaNickname, vistaSala, vistaRonda):
        self.main_window = main_window

        # Guardar referencias a controladores
        self.controlador_nickname = controlador_nickname
        self.controlador_sala = controlador_sala
        self.controlador_ronda = controlador_ronda

        # Guardar referencias a vistas
        self.vistaNickname = vistaNickname
        self.vistaSala = vistaSala
        self.vistaRonda = vistaRonda

        # Agregar vistas al stack
        self.vistaNickname_Index = self.main_window.stack.addWidget(self.vistaNickname)
        self.vistaSala_Index = self.main_window.stack.addWidget(self.vistaSala)
        self.vistaRonda_Index = self.main_window.stack.addWidget(self.vistaRonda)
      # --- Métodos de navegación ---
      #  Cada método cambia la vista actual del stack a la vista correspondiente, metodo unico para favorecer desacoplamiento
    
    def mostrar(self, eleccion: str):
        if eleccion == "nickname":
            self.main_window.stack.setCurrentIndex(self.vistaNickname_Index)
        elif eleccion == "sala":
            self.main_window.stack.setCurrentIndex(self.vistaSala_Index)
        elif eleccion == "ronda":
            self.main_window.stack.setCurrentIndex(self.vistaRonda_Index)
        elif eleccion == "resultados":
            pass
            #self.main_window.stack.setCurrentIndex(self.vistaResultados_Index)
        else:
            raise ValueError(f"Vista '{eleccion}' no encontrada")