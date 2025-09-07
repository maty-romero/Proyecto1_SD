""""
    Clase esqueleto para ejecucion de procedimientos
    remotos desde Server
"""
import Pyro5.api
import os
import json

from AbstractGUI import AbstractGUI

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

        ronda_data = json.loads(info)
        nro_ronda = ronda_data["nro_ronda"]
        votos_cliente = {"nro_ronda": nro_ronda, "votos": {}}

        # Recorre todas las respuestas y permite al cliente votar
        for jugador, categorias in ronda_data["respuestas"].items():
            votos_cliente["votos"][jugador] = {}
            for categoria, resp in categorias.items():
                respuesta_txt = resp["respuesta"]
                self.gui.show_message(
                    f"¿Es válida la respuesta '{respuesta_txt}' de {jugador} en {categoria}? (s/n)"
                )
                voto = input().lower().startswith("s")
                votos_cliente["votos"][jugador][categoria] = voto

        # Envia votos al servidor || ¿Debería encargarse de eso acá?
        proxy_gestor = Pyro5.api.Proxy("PYRONAME:gestor.partida")
        proxy_gestor.registrar_votos(votos_cliente)