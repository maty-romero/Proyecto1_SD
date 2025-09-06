from Main.Cliente.GestorCliente import GestorCliente
from Main.Common.ConsoleGUI import ConsoleGUI

# equivalente a Main Server
if __name__ == "__main__":
    gestor = GestorCliente(gui=ConsoleGUI())
    gestor.ingresar_nickname_valido()
    gestor.unirse_a_sala()
    # Uso de gestor Cliente Para Jugar