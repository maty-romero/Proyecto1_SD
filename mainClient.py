from Cliente.Modelos.GestorCliente import GestorCliente
from Cliente.Controladores.ControladorNickname import ControladorNickName
from PyQt6 import QtWidgets

if __name__ == "__main__":
    # Uso de gestorCliente Para Jugar
    import sys
    app = QtWidgets.QApplication(sys.argv)
    gestor = GestorCliente() # Pasarle gestor al controlador como parámetro
    controlador = ControladorNickName(gestor)
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