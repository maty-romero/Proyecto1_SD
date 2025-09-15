""""
    Clase esqueleto para ejecucion de procedimientos
    remotos desde Server
"""
import Pyro5.api
import threading
from Main.Common.AbstractGUI import AbstractGUI

@Pyro5.api.expose
class ServicioCliente:
    def __init__(self, gui: AbstractGUI, gestor):
        self.gui = gui
        self.gestor = gestor  # referencia al GestorCliente

    def recibir_info_ronda(self, info: str):
        threading.Thread(target=self.gestor.on_info, args=("ronda", info), daemon=True).start()


    def obtener_respuesta_memoria(self) -> str:
        # Metodo expuesto para que el server pida información del cliente
        return self.gestor.provide_response()

    """

        def recibir_info_sala(self, info: str):
            # Limpiar la consola / GUI
            try:
                self.gui.clear()
            except Exception:
                pass
            #self.gui.show_message("**[recibir_info_sala]**")
            #self.gui.show_message(f"Server mandó mensaje!\n📨 Mensaje: {info}")

            # Delegar lógica al gestor (no hacer trabajo pesado aquí)
            # Ejecutamos en hilo para no bloquear el hilo del daemon de Pyro
            threading.Thread(target=self.gestor.on_info, args=("sala", info), daemon=True).start()

            def recibir_info_confirmar_jugador(self, info: str):
                threading.Thread(target=self.gestor.on_info, args=("sala_confirmacion", info), daemon=True).start()

        """