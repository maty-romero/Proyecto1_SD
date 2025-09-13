from PyQt6 import QtWidgets
from vistas.Puntajes import Ui_MainWindow



class ControladorPuntajes:

    def __init__(self,partida):
        # Inicializa la ventana principal
        self.MainWindow = QtWidgets.QMainWindow()
        self.__vista = Ui_MainWindow()
        self.__vista.setupUi(self.MainWindow)
        
        # Guardar la instancia de partida
        self.partida = partida
        
        # Actualizar las etiquetas de puntajes con la información de la ronda y la letra
        self.actualizar_vista_puntajes()
        
        
        self.MainWindow.show()
        
    def actualizar_vista_puntajes(self):
        # Obtener la ronda y la letra de la misma instancia de partida
        numero_ronda = self.partida.get_nro_ronda()
        numero_ronda_actual = self.partida.get_ronda_actual()
        letra = self.partida.get_letra_random()

        # Actualizar las etiquetas de la vista con el número de ronda y la letra
        self.__vista.labelRondaConNumero.setText(f"Ronda: {numero_ronda_actual}/{numero_ronda}")
        self.__vista.labelLetraRandom.setText(f"Letra: {letra}")
        
        
