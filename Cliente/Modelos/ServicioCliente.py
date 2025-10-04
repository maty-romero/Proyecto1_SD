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
        
