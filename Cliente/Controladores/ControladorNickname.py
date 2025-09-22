from PyQt6 import QtWidgets
#from Modelos.GestorCliente import GestorCliente
from Cliente.A_Vistas.VistaNickname import VistaNickname
from Cliente.Controladores.ControladorSala import ControladorSala

class ControladorNickName:
    def __init__(self, vista: 'VistaNickname', gestor_cliente):
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente = gestor_cliente

        # Conectar señal del botón Ingresar
        self.vista.getIngresarbtn().clicked.connect(self.ingresarPartida)

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion

    def reset(self):
        """Limpia los campos de la vista."""
        self.vista.textEdit.clear()

    def ingresarPartida(self):
        """Verifica y registra el nickname, luego navega a la sala."""
        existe_partida = self.gestor_cliente.buscar_partida()
        if not existe_partida:
            # Opcional: mostrar mensaje si no hay partida
            return

        nickname = self.vista.getNickname()
        formated_nickname = nickname.lower().replace(" ", "")

        valido = self.gestor_cliente.ingresar_nickname_valido(formated_nickname)
        if valido['exito']:
            # Mostrar mensaje de éxito
            self.vista.aviso_nickName_exitoso(formated_nickname)
            # Unirse a la sala
            self.gestor_cliente.unirse_a_sala(formated_nickname)
             # Navegar a la sala
            self.navegacion.mostrar("sala")
            # Actualizar el nombre en la vista de sala
            self.navegacion.controlador_sala.actualizar_nombre_jugador()
            self.gestor_cliente.logger.info("FINALIZO EL UNIRSE A SALA")
            self.gestor_cliente.logger.info(self.gestor_cliente.Jugador_cliente)

            # Navegar a la vista Sala usando el controlador de navegación
            self.navegacion.mostrar("sala")
        else:
            # Mostrar mensaje de error
            self.vista.aviso_nickName_repetido(formated_nickname)
