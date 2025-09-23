from Cliente.Modelos.GestorCliente import GestorCliente
from Cliente.Controladores.ControladorNickname import ControladorNickName
from PyQt6 import QtWidgets
import sys
from PyQt6 import QtWidgets
from Cliente.A_Vistas.VistaNickname import VistaNickname
from Cliente.A_Vistas.VistaSala import VistaSala
from Cliente.A_Vistas.VistaRonda import VistaRonda
from Cliente.Controladores.ControladorNavegacion import ControladorNavegacion
from Cliente.Controladores.ControladorNickname import ControladorNickName
from Cliente.Controladores.ControladorSala import ControladorSala
from Cliente.Controladores.ControladorRonda import ControladorRonda
from Cliente.Modelos.GestorCliente import GestorCliente
from Cliente.A_Vistas.MainWindow import MainWindow

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # Ventana principal con stack
    main_window = MainWindow()

    # Crear gestor de cliente
    gestor = GestorCliente()

    # Crear vistas
    vista_nickname = VistaNickname()
    vista_sala = VistaSala()
    vista_ronda = VistaRonda()

    # Crear controladores de vistas
    controlador_nickname = ControladorNickName(
        vista_nickname,
        gestor
    )

    controlador_sala = ControladorSala(
        vista_sala,
        gestor
    )

    controlador_ronda = ControladorRonda(
        vista_ronda,
        gestor
    )

    # Crear controlador de navegación
    controlador_navegacion = ControladorNavegacion(
        main_window,
        controlador_nickname,
        controlador_sala,
        controlador_ronda,
        vista_nickname,
        vista_sala,
        vista_ronda
    )
    controlador_nickname.setNavegacion(controlador_navegacion)
    controlador_sala.setNavegacion(controlador_navegacion)
    controlador_ronda.setNavegacion(controlador_navegacion)

    gestor.registrar_controlador_navegador(controlador_navegacion) # Para referncias a cambios
    # Mostrar vista inicial
    controlador_navegacion.mostrar("nickname")

    sys.exit(app.exec())

    # existe_partida = gestor.buscar_partida()
    # if (existe_partida):
    #     # gestor.ingresar_nickname_valido() ##Este método se invoca en el ControladorNickname, pasandole por parámetro el nombre formateado
    #     gestor.logger.info("FINALIZO EL UNIRSE A SALA")
    #     gestor.logger.info(gestor.Jugador_cliente)
    #     gestor.confirmar_jugador_partida(gestor.Jugador_cliente.get_nickname())
    
    """
    existe_partida = gestor.buscar_partida()
    if (existe_partida):
        gestor.ingresar_nickname_valido()
        gestor.unirse_a_sala()
        gestor.confirmar_jugador_partida()
    """