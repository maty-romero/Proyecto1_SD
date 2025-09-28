from Cliente.A_Vistas.VistaMensajeTransitorio import VistaMensajeTransitorio
from Cliente.A_Vistas.VistaVotaciones import VistaVotaciones
from Cliente.Controladores.ControladorVotaciones import ControladorVotaciones
from Cliente.Modelos.GestorCliente import GestorCliente
from Cliente.Controladores.ControladorNickname import ControladorNickName
from PyQt6 import QtWidgets
import sys
from PyQt6 import QtWidgets
from Cliente.A_Vistas.VistaNickname import VistaNickname
from Cliente.A_Vistas.VistaSala import VistaSala
from Cliente.A_Vistas.VistaRonda import VistaRonda
from Cliente.A_Vistas.VistaResultados import VistaResultados
from Cliente.Controladores.ControladorNavegacion import ControladorNavegacion
from Cliente.Controladores.ControladorNickname import ControladorNickName
from Cliente.Controladores.ControladorSala import ControladorSala
from Cliente.Controladores.ControladorRonda import ControladorRonda
from Cliente.Controladores.ControladorResultados import ControladorResultados
from Cliente.Controladores.ControladorMensajeTransitorio import ControladorMensajeTransitorio
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
    vista_votaciones = VistaVotaciones()
    vista_resultados=VistaResultados()
    vista_mensaje = VistaMensajeTransitorio()
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

    controlador_votaciones = ControladorVotaciones(
        vista_votaciones,
        gestor
    )
    
    controlador_resultados= ControladorResultados(
        vista_resultados,
        gestor
    )

    controlador_mensaje = ControladorMensajeTransitorio(
        vista_mensaje, gestor
    )

    # Crear controlador de navegación
    controlador_navegacion = ControladorNavegacion(
        main_window=main_window,
        controlador_nickname=controlador_nickname,
        controlador_sala=controlador_sala,
        controlador_ronda=controlador_ronda,
        vistaNickname=vista_nickname,
        vistaSala=vista_sala,
        vistaRonda=vista_ronda,
        controlador_votaciones=controlador_votaciones,
        vistaVotaciones=vista_votaciones,
        controlador_resultados=controlador_resultados,
        vistaResultados=vista_resultados,
        controlador_mensaje= controlador_mensaje ,
        vistaMensaje= vista_mensaje
    )
    
    controlador_nickname.setNavegacion(controlador_navegacion)
    controlador_sala.setNavegacion(controlador_navegacion)
    controlador_ronda.setNavegacion(controlador_navegacion)
    controlador_votaciones.setNavegacion(controlador_navegacion)
    controlador_resultados.setNavegacion(controlador_navegacion)
    controlador_mensaje.setNavegacion(controlador_navegacion)

    gestor.set_controlador_navegacion(controlador_navegacion)

    # Mostrar vista inicial
    controlador_navegacion.mostrar("nickname")
    #controlador_navegacion.mostrar("mensaje") # Para Probar vistaVotaciones
    #controlador_navegacion.mostrar("resultados") # Para Probar vistaVotaciones

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