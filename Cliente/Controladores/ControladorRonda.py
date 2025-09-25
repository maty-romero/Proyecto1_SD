from PyQt6 import QtWidgets
from Cliente.A_Vistas.VistaRonda import VistaRonda
from Cliente.Modelos.Respuesta import Respuesta
from Cliente.Modelos.RondaCliente import RondaCliente

class ControladorRonda:
    def __init__(self, vista: 'VistaRonda', gestor_cliente):
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente = gestor_cliente

        # Mostrar info inicial de la ronda
        #self.mostrar_info_ronda()

        # Conectar botón STOP! a la acción correspondiente
        self.vista.enviar_respuestas_btn.clicked.connect(self.finalizar_ronda)

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion

    def reset(self):
        """Limpia los campos de la vista."""
        inputs = self.vista.obtener_categorias_input()
        for input in inputs:
            input.clear()

    def mostrar_info_ronda(self):
        """Actualiza las etiquetas y categorías según la info de la sala"""
        self.reset()
        info = self.gestor_cliente.get_info_ronda_act()
        categorias = info.get('categorias', [])
        ronda = info.get('nro_ronda', 1)
        total_rondas = info.get('total_rondas', 3)

        # Actualizar número de ronda y letra (si aplica)
        self.vista.set_numero_ronda(ronda, total_rondas)
        if 'letra_ronda' in info:
            self.vista.setLetraAleatoria(info['letra_ronda'])

        # Actualizar categorías
        inputs_categorias = self.vista.obtener_categorias_label()
        for categoria_text, input_widget in zip(categorias, inputs_categorias):
            input_widget.setText(categoria_text)

    def finalizar_ronda(self):
        """Acción al presionar STOP!"""
        self.gestor_cliente.enviar_stop()


    def obtener_respuestas(self):
        respuestas = [input_widget.text() for input_widget in self.vista.obtener_categorias_input()]
        proxy_para_pedir_info = self.gestor_cliente.get_proxy_partida()
        proxy_para_pedir_info._pyroClaimOwnership()
        info = proxy_para_pedir_info.get_info_ronda_actual()
        categorias = info.get('categorias', [])
        nickname = self.gestor_cliente.Jugador_cliente.to_dict()['nickname']
        ronda = RondaCliente(categorias, nickname )
        for cat, res in zip(categorias, respuestas):
            ronda.agregarRespuesta(Respuesta(cat, res))

        info_respuestas = ronda.getRespuestasJugador()
        return info_respuestas
   