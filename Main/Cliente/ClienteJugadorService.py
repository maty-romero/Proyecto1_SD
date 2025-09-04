""""
    Clase esqueleto para ejecucion de procedimientos
    remotos desde Server
"""
import Pyro5.api

from Main.Common.AbstractGUI import AbstractGUI

@Pyro5.api.expose
class ClienteJugadorService:
    def __init__(self, gui: AbstractGUI):
        self.gui = gui

    def recibir_info_sala(self, info: str):
        # Limpiar la consola -- No limpia
        self.gui.clear() # limpia consola o pantalla 
        #os.system('cls' if os.name == 'nt' else 'clear')
        self.gui.show_message("**[recibir_info_sala]**")
        # Mostrar el mensaje recibido
        self.gui.show_message(f"Server mandó mensaje!\n📨 Mensaje: {info}")

    def recibir_info_ronda(self,info: str):
        self.gui.show_message("**[recibir_info_ronda]**")
        # Mostrar el mensaje recibido
        self.gui.show_message(f"Server mandó mensaje!\n📨 Mensaje: {info}")