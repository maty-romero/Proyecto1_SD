from PyQt6 import QtWidgets

from Cliente.A_Vistas.SalaView import Ui_SalaView
from Cliente.Controladores.ControladorRonda import ControladorRonda

class ControladorSalaView:

    def __init__(self, gestor_cliente):
        # Inicializa la ventana principal
        self.gestor_cliente = gestor_cliente
        self.gestor_cliente.set_controlador_actual(self)
        self.MainWindow = QtWidgets.QMainWindow()
        self.vista = Ui_SalaView()
        self.vista.setupUi(self.MainWindow)
    
        # # Conectar botones a eventos
        # self.vista.clicked.connect(self.confirmar_jugador)
        
        # # Inicialmente, deshabilitar el botón
        # self.vista.confirmar_jugador_btn.setEnabled(False)
        
        self.vista.getUnirSala().clicked.connect(self.irRonda)

        # Obtener el nickname del jugador desde 'Jugador_cliente' 
        nickname = self.gestor_cliente.Jugador_cliente.to_dict()['nickname']
        self.vista.setNombreJugador(str(nickname))
        
        self.mostrar_info_sala()

        self.MainWindow.show()


    def irRonda(self):
        self.gestor_cliente.confirmar_jugador_partida()
        self.vista.setEstadoSala("Jugador confirmado. Esperando jugadores...")# estado estático, debería venir del servidor la info
        
        # self.MainWindow.close()
        # self.controlador_Ronda = ControladorRonda(self.gestor_cliente)
        # self.gestor_cliente.set_controlador_actual(self.controlador_Ronda)
    
    def mostrar_vista_ronda(self):
        self.MainWindow.close()
        self.controlador_Ronda = ControladorRonda(self.gestor_cliente)
        self.gestor_cliente.set_controlador_actual(self.controlador_Ronda)

    def mostrar_info_sala(self):
        #PENDIENTE: Obtener el estado de la sala, ¿dónde se obtiene?
        info = self.gestor_cliente.get_info_sala()
        self.vista.setRonda(str(info['rondas']))
        categorias = ", ".join(info["categorias"])
        self.vista.setListaCategoria(categorias)
        #self.vista.setEstadoSala("Esperando jugadores...")# estado Dinamico
        
        dict_jugadores = self.gestor_cliente.proxy_partida.ver_jugadores_partida()
        #jugadores = "\n".join(dict_jugadores.keys())
        jugadores = ",".join(dict_jugadores.keys())
        self.vista.setListaJugadores(jugadores)

        self.vista.setJugadoresRequeridos(str(self.gestor_cliente.get_jugadores_minimos()))

    
    
    