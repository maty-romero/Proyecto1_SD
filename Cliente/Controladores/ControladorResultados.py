from PyQt6 import QtWidgets
from Cliente.A_Vistas.VistaResultados import VistaResultados

from PyQt6.QtWidgets import QWidget

from Cliente.Modelos import GestorCliente
from Cliente.Utils.ConsoleLogger import ConsoleLogger


class ControladorResultados:
    def __init__(self, vista: 'VistaResultados', gestor_cliente):
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente: GestorCliente = gestor_cliente
        #self.logger = ConsoleLogger(name="ControladorResultados", level="INFO")
        
    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion
        
    def mostrar_resultados(self, resultados):
        # Los resultados ya vienen como parámetro desde el servidor
        self.vista.set_jugadores(resultados['jugadores'])
        self.vista.set_puntajes_totales(resultados['puntajes_totales']) # 'fiore':2, 'day':1
        self.vista.set_ganador(resultados['ganador'])
        


    