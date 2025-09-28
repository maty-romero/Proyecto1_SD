from PyQt6 import QtWidgets
from Cliente.A_Vistas.VistaMensajeTransitorio import VistaMensajeTransitorio

from PyQt6.QtWidgets import QWidget

from Cliente.Modelos import GestorCliente
from Cliente.Utils.ConsoleLogger import ConsoleLogger


class ControladorMensajeTransitorio:
    def __init__(self, vista: 'VistaMensajeTransitorio', gestor_cliente):
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente: GestorCliente = gestor_cliente
        #self.logger = ConsoleLogger(name="ControladorResultados", level="INFO")
        
        self.vista.boton_si.clicked.connect(self.accion_si)
        self.vista.boton_no.clicked.connect(self.accion_no)

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion

    def accion_si(self):
        self.navegacion.mostrar("vista_si")

    def accion_no(self):
        self.navegacion.mostrar("vista_no")

