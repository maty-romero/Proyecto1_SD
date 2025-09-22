from PyQt6 import QtWidgets
#from Modelos.GestorCliente import GestorCliente
from Cliente.A_Vistas.vistaIngresarNickname import Ui_MainWindow
from Cliente.Controladores.ControladorSalaView import ControladorSalaView

class ControladorNickName:

    def __init__(self, gestor_cliente):
        # Inicializa la ventana principal
        self.MainWindow = QtWidgets.QMainWindow()
        self.vista = Ui_MainWindow()
        self.vista.setupUi(self.MainWindow)
        self.gestor_cliente = gestor_cliente
        self.MainWindow.show()
        self.vista.getIngresarbtn().clicked.connect(self.ingresarPartida)

    
    def ingresarPartida(self):
        # Verificar si existe una partida activa
        existe_partida = self.gestor_cliente.buscar_partida()
        if (existe_partida):
            # Obtener el nickname del campo de texto
            nickname = self.vista.getNickname()
            formated_nickname = nickname.lower().replace(" ", "") # Elimina espacios y convierte a minúsculas
            # Verificar si el nickname está disponible
            valido = self.gestor_cliente.ingresar_nickname_valido(formated_nickname)
            if valido['exito'] == True:
                # Mostrar el mensaje de éxito
                self.vista.aviso_nickName_exitoso(formated_nickname)
                # Unirse a la sala
                self.gestor_cliente.unirse_a_sala(formated_nickname)
                self.gestor_cliente.logger.info("FINALIZO EL UNIRSE A SALA")
                self.gestor_cliente.logger.info(self.gestor_cliente.Jugador_cliente)
                # self.gestor_cliente.confirmar_jugador_partida()

                self.MainWindow.close()
                self.controladorSala = ControladorSalaView(self.gestor_cliente)
                

            else:
                # Si el nickname no es válido, mostramos el mensaje de error en la vista
                self.vista.aviso_nickName_repetido(formated_nickname)

        #conectar el metodo de registrar el nickname (que está por consola)
        #mostrar el nombre en la vista de la sala
