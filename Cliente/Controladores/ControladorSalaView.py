from PyQt6 import QtWidgets
from Vistas.testVistas.SalaView import Ui_SalaView


class ControladorSala:

    def __init__(self):
        # Inicializa la ventana principal
        self.MainWindow = QtWidgets.QMainWindow()
        self.vista = Ui_SalaView()
        self.vista.setupUi(self.MainWindow)
    
        # # Conectar botones a eventos
        # self.vista.clicked.connect(self.confirmar_jugador)
        
        # # Inicialmente, deshabilitar el botón
        # self.vista.confirmar_jugador_btn.setEnabled(False)
        
        self.vista.confirmar_jugador_btn.clicked.connect(self.mostrar_jugador)

        self.MainWindow.show()

        
    def mostrar_jugador(self):
        print(self.vista.getNombreJugador())
        # Cerrar la ventana actual (votaciones)
        # self.MainWindow.close()
        # Crear y mostrar la ventana de puntajes
        #self.controlador_puntajes = ControladorRonda()
    