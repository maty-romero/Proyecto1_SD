import os
from Main.Common.AbstractGUI import AbstractGUI

class ConsoleGUI(AbstractGUI):
    def show_message(self, message: str) -> None:
        print(f"[INFO] {message}")

    def get_input(self, prompt: str) -> str:
        return input(f"{prompt}")

    def show_error(self, error: str) -> None:
        print(f"[ERROR] {error}")

    def clear(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')


"""
    ** Ejemplo uso de la Abstraccion - Por Inyeccion de dependencias
    
    class Application:
    def __init__(self, gui: AbstractGUI):
        self.gui = gui

    def run(self):
        self.gui.clear()
        self.gui.show_message("Bienvenido a la aplicación distribuida")
        name = self.gui.get_input("Ingrese su nombre")
        if not name:
            self.gui.show_error("El nombre no puede estar vacío")
        else:
            self.gui.show_message(f"Hola, {name}!")

    -----------------

    if __name__ == "__main__":
        gui = ConsoleGUI()
        app = Application(gui)
        app.run()
        
"""