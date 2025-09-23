from PyQt6 import QtWidgets
from Cliente.A_Vistas.VistaSala import VistaSala
from Cliente.Controladores.ControladorRonda import ControladorRonda

from PyQt6.QtWidgets import QWidget

class ControladorSala:
    def __init__(self, vista: 'VistaSala', gestor_cliente):
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente = gestor_cliente

        # Conectar botón "Estoy Listo!" a la acción correspondiente
        self.vista.getUnirSala().clicked.connect(self.ir_a_ronda)

        # Mostrar info de la sala
        # self.mostrar_info_sala() -- Esto queda comentado porque se utiliza en ControladorNavegación

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion
        
    def actualizar_nombre_jugador(self):
        if self.gestor_cliente.Jugador_cliente is not None:
            nickname = self.gestor_cliente.Jugador_cliente.to_dict()['nickname']
            self.vista.setNombreJugador(nickname)

    def ir_a_ronda(self):
        """Navega a la vista de Ronda usando el controlador de navegación"""
        self.gestor_cliente.confirmar_jugador_partida()
        self.navegacion.mostrar("ronda")
        #Acá no debería ir directo a ronda sino que debería actualizar el estado de la sala y esperar a los otros jugadores

    def mostrar_info_sala(self):
        """Actualiza la vista con la información de la sala"""
        info = self.gestor_cliente.get_info_sala()
        self.vista.setRonda(str(info.get('rondas', 0)))
        categorias = ", ".join(info.get('categorias', []))
        self.vista.setListaCategoria(categorias)
        self.vista.setEstadoSala("Esperando jugadores...")

        dict_jugadores = self.gestor_cliente.get_jugadores_en_sala()
        jugadores = ", ".join(dict_jugadores.keys())
        self.vista.setListaJugadores(jugadores)

        self.vista.setJugadoresRequeridos(str(self.gestor_cliente.get_jugadores_minimos()))

