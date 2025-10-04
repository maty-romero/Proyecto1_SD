from PyQt6 import QtWidgets
from Cliente.A_Vistas.VistaMensajeTransitorio import VistaMensajeTransitorio

from PyQt6.QtWidgets import QWidget

from Cliente.Modelos import GestorCliente
from Utils.ConsoleLogger import ConsoleLogger


class ControladorMensajeTransitorio:
    def __init__(self, vista: 'VistaMensajeTransitorio', gestor_cliente):
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente: GestorCliente = gestor_cliente
        self.logger = ConsoleLogger(name="ControladorMensajeTransitorio", level="INFO")
        

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion


    def mostrar_mensaje_reconexion(self, titulo: str, mensaje: str, mostrar_botones: bool = True):
        """Muestra mensaje de reconexión con opciones personalizadas"""
        self.vista.setMensaje(f"{titulo}\n\n{mensaje}")
        


