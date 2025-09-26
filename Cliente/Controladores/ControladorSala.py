from PyQt6 import QtWidgets
from Cliente.A_Vistas.VistaSala import VistaSala
from Cliente.Controladores.ControladorRonda import ControladorRonda

from PyQt6.QtWidgets import QWidget

from Cliente.Modelos import GestorCliente
from Cliente.Utils.ConsoleLogger import ConsoleLogger


class ControladorSala:
    def __init__(self, vista: 'VistaSala', gestor_cliente):
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente: GestorCliente = gestor_cliente
        self.logger = ConsoleLogger(name="ControladorSala", level="INFO")

        # Conectar botón "Estoy Listo!" a la acción correspondiente
        self.vista.getUnirSala().clicked.connect(self.confirmar_y_esperar)

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion
        
    def actualizar_nombre_jugador(self):
        if self.gestor_cliente.Jugador_cliente is not None:
            nickname = self.gestor_cliente.Jugador_cliente.to_dict()['nickname']
            self.vista.setNombreJugador(nickname)

    # Confirma Jugador y Espera a que sean N Jugadores Confirmados o Listos
    def confirmar_y_esperar(self):
        """Navega a la vista de Ronda usando el controlador de navegación"""
        self.vista.getUnirSala().setEnabled(False)
        self.gestor_cliente.confirmar_jugador_partida()
        self.vista.setEstadoSala("Esperando que confirmen jugadores...")

    def mostrar_info_sala(self):
        """Actualiza la vista con la información de la sala"""
        info: dict = self.gestor_cliente.get_proxy_partida_singleton().obtener_info_sala()
        self.vista.setRonda(str(info.get('rondas', 0)))
        categorias = ", ".join(info.get('categorias', []))
        self.vista.setListaCategoria(categorias)
        self.vista.setEstadoSala("")

        jugadores_conectados: list[str] = self.gestor_cliente.get_proxy_partida_singleton().obtener_jugadores_en_partida()
        self.logger.warning(f"jugadores_conectados: {jugadores_conectados}")
        jugadores_str = ", ".join(jugadores_conectados)
        self.vista.setListaJugadores(jugadores_str)
        self.vista.setJugadoresRequeridos(str(self.gestor_cliente.get_jugadores_min()))


    def cambiar_estado_sala(self, msg: str):
        """Actualiza la vista con la union de nuevos jugadores"""
        self.logger.warning(f"Cambio_estado_sala, msg: {msg}")
        """
            LINEA PROVISORIA PARA PROBAR CON MULTIPLES CLIENTES EN UNA MISMA MAQUINA 
            (UTILIZANDO SIMULACION DE MULTIPLES CLIENTES EN UNIRSE SALA - GESTOR CLIENTE)
        """
        #self.gestor_cliente.proxy_partida._pyroClaimOwnership()
        jugadores_conectados: list[str] = self.gestor_cliente.get_proxy_partida_singleton().obtener_jugadores_en_partida()
        jugadores_str = ", ".join(jugadores_conectados)
        self.vista.setListaJugadores(jugadores_str)

        self.vista.setEstadoSala(msg)

        self.vista.setJugadoresRequeridos(str(self.gestor_cliente.get_jugadores_min()))

