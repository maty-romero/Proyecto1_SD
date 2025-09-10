import sys
from sysconfig import get_scheme_names

from Main.Cliente.GestorCliente import GestorCliente
from Main.Common.ConsoleGUI import ConsoleGUI

if __name__ == "__main__":
    # Uso de gestorCliente Para Jugar
    gestor = GestorCliente(gui=ConsoleGUI())

    existe_partida = gestor.buscar_partida()
    if (existe_partida):
        gestor.ingresar_nickname_valido()
        gestor.unirse_a_sala()
        gestor.confirmar_jugador_partida()


