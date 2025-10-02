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
        
        self.vista.boton_si.clicked.connect(self.accion_si)
        self.vista.boton_no.clicked.connect(self.accion_no)

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion

    def accion_si(self):
        self.navegacion.mostrar("vista_si")

    def accion_no(self):
        self.navegacion.mostrar("vista_no")

    def mostrar_mensaje_reconexion(self, titulo: str, mensaje: str, mostrar_botones: bool = True):
        """Muestra mensaje de reconexión con opciones personalizadas"""
        self.vista.setMensaje(f"{titulo}\n\n{mensaje}")
        
        # if mostrar_botones:
        #     self.vista.boton_si.show()
        #     self.vista.boton_no.show()
        #     self.vista.boton_si.setText("Reintentar")
        #     self.vista.boton_no.setText("Salir")
        # else:
        #     self.vista.boton_si.hide()
        #     self.vista.boton_no.hide()
        
        # # Auto-ocultar si se especifica
        # if auto_ocultar > 0:
        #     import threading
        #     import time
        #     def auto_hide():
        #         time.sleep(auto_ocultar)

        #         if hasattr(self, 'navegacion'):
        #             # Ocultar la vista de mensaje transitorio
        #             self.vista.hide()
            
        #     threading.Thread(target=auto_hide, daemon=True).start()

