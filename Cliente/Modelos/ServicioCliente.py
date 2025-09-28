""""
    Clase esqueleto para ejecucion de procedimientos
    remotos desde Server
"""
import Pyro5.api
import threading

@Pyro5.api.expose
class ServicioCliente:
    def __init__(self, gestor):
        self.gestor = gestor  # referencia al GestorCliente

    def recibir_info_ronda(self, info: str):
        threading.Thread(target=self.gestor.on_info, args=("ronda", info), daemon=True).start()

    def obtener_respuesta_memoria(self) -> str:
        # Metodo expuesto para que el server pida información del cliente
        return self.gestor.provide_response()

    def actualizar_vista_votacion(self, respuestas_clientes):
        self.gestor.cargar_datos_vista_votacion(respuestas_clientes)

    def obtener_votos_cliente(self) -> dict:
        return self.gestor.enviar_votos_jugador()

    def mostrar_vista_desconexion(self):
        print(f"2. [DEBUG] Desde ServicioCliente se mostrará la vista de desconexion: {threading.current_thread().name}")
        self.gestor.mostrar_vista_desconexion()

        
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