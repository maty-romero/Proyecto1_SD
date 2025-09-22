from PyQt6 import QtWidgets
from Cliente.A_Vistas.RondaView import Ui_RondaView
from Cliente.A_Vistas.RondaView import Ui_RondaView

import threading
from PyQt6.QtCore import QTimer

class ControladorRonda:

    def __init__(self, gestor_cliente):
        # Inicializa la ventana principal
        self.MainWindow = QtWidgets.QMainWindow()
        self.vista = Ui_RondaView()
        self.vista.setupUi(self.MainWindow)
        self.gestor_cliente = gestor_cliente
        
        self.mostrar_info_ronda()
        self.MainWindow.show()
       

    def mostrar_info_ronda(self):
        info = self.gestor_cliente.get_info_sala()#info= ronda y categorias
        categorias = info['categorias']
        label_categorias = self.vista.obtener_categorias() 
        for categoria, label in zip(categorias,label_categorias):
            label.setText(categoria)
    
