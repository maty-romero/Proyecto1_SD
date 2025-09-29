from PyQt6 import QtWidgets
from Cliente.A_Vistas.VistaSala import VistaSala
from Cliente.Controladores.ControladorRonda import ControladorRonda

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from Cliente.Modelos import GestorCliente
from Utils.ConsoleLogger import ConsoleLogger
import threading
import Pyro5.api


class ControladorSala(QObject):
    # Signal para actualizar UI desde cualquier hilo
    actualizar_sala_signal = pyqtSignal(dict, list)
    
    def __init__(self, vista: 'VistaSala', gestor_cliente):
        super().__init__()
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente: GestorCliente = gestor_cliente
        self.logger = ConsoleLogger(name="ControladorSala", level="INFO")
        
        # Conectar signal a slot
        self.actualizar_sala_signal.connect(self._actualizar_vista_sala)

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
        """Actualiza la vista con la información de la sala - Thread-safe"""
        if threading.current_thread() == threading.main_thread():
            # Si estamos en el hilo principal, llamar directamente
            self._mostrar_info_sala_internal()
        else:
            # Si estamos en otro hilo, obtener datos y usar signal
            try:
                # Crear nuevo proxy para este hilo
                proxy = Pyro5.api.Proxy(self.gestor_cliente.get_proxy_partida_singleton()._pyroUri)
                info = proxy.obtener_info_sala()
                jugadores_conectados = proxy.obtener_jugadores_en_partida()
                
                # Emitir signal con los datos
                self.actualizar_sala_signal.emit(info, jugadores_conectados)
            except Exception as e:
                self.logger.error(f"Error obteniendo info de sala desde hilo secundario: {e}")
                # Fallback: intentar desde hilo principal
                QTimer.singleShot(0, self._mostrar_info_sala_internal)
    
    def _mostrar_info_sala_internal(self):
        """Método interno para actualizar vista (solo desde hilo principal)"""
        try:
            info: dict = self.gestor_cliente.get_proxy_partida_singleton().obtener_info_sala()
            jugadores_conectados: list[str] = self.gestor_cliente.get_proxy_partida_singleton().obtener_jugadores_en_partida()
            self._actualizar_vista_sala(info, jugadores_conectados)
        except Exception as e:
            self.logger.error(f"Error obteniendo info de sala: {e}")
    
    def _actualizar_vista_sala(self, info: dict, jugadores_conectados: list):
        """Actualiza los elementos de la vista con los datos proporcionados"""
        self.vista.setRonda(str(info.get('rondas', 0)))
        categorias = ", ".join(info.get('categorias', []))
        self.vista.setListaCategoria(categorias)
        self.vista.setEstadoSala("")
        
        self.logger.warning(f"jugadores_conectados: {jugadores_conectados}")
        jugadores_str = ", ".join(jugadores_conectados)
        self.vista.setListaJugadores(jugadores_str)
        self.vista.setJugadoresRequeridos(str(self.gestor_cliente.get_jugadores_min()))


    def cambiar_estado_sala(self, msg: str):
        """Actualiza la vista con la union de nuevos jugadores - Thread-safe"""
        self.logger.warning(f"Cambio_estado_sala, msg: {msg}")
        
        if threading.current_thread() == threading.main_thread():
            # Hilo principal: usar proxy existente
            try:
                jugadores_conectados: list[str] = self.gestor_cliente.get_proxy_partida_singleton().obtener_jugadores_en_partida()
                jugadores_str = ", ".join(jugadores_conectados)
                self.vista.setListaJugadores(jugadores_str)
                self.vista.setEstadoSala(msg)
                self.vista.setJugadoresRequeridos(str(self.gestor_cliente.get_jugadores_min()))
            except Exception as e:
                self.logger.error(f"Error en cambiar_estado_sala desde hilo principal: {e}")
        else:
            # Hilo secundario: crear nuevo proxy
            try:
                proxy = Pyro5.api.Proxy(self.gestor_cliente.get_proxy_partida_singleton()._pyroUri)
                jugadores_conectados = proxy.obtener_jugadores_en_partida()
                
                # Usar QTimer para actualizar UI desde hilo principal
                QTimer.singleShot(0, lambda: self._actualizar_estado_ui(msg, jugadores_conectados))
            except Exception as e:
                self.logger.error(f"Error en cambiar_estado_sala desde hilo secundario: {e}")
    
    def _actualizar_estado_ui(self, msg: str, jugadores_conectados: list):
        """Actualiza la UI con el estado y jugadores (solo desde hilo principal)"""
        jugadores_str = ", ".join(jugadores_conectados)
        self.vista.setListaJugadores(jugadores_str)
        self.vista.setEstadoSala(msg)
        self.vista.setJugadoresRequeridos(str(self.gestor_cliente.get_jugadores_min()))

