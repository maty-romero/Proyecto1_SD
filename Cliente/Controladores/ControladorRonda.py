from PyQt6 import QtWidgets
from Cliente.A_Vistas.VistaRonda import VistaRonda

class ControladorRonda:
    def __init__(self, vista: 'VistaRonda', gestor_cliente):
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente = gestor_cliente

        # Mostrar info inicial de la ronda
        self.mostrar_info_ronda()

        # Conectar botón STOP! a la acción correspondiente
        self.vista.enviar_respuestas_btn.clicked.connect(self.finalizar_ronda)

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion

    def mostrar_info_ronda(self):
        """Actualiza las etiquetas y categorías según la info de la sala"""
        info = self.gestor_cliente.get_info_sala()
        categorias = info.get('categorias', [])
        ronda = info.get('ronda_actual', 1)
        total_rondas = info.get('total_rondas', 3)

        # Actualizar número de ronda y letra (si aplica)
        self.vista.set_numero_ronda(ronda, total_rondas)
        if 'letra' in info:
            self.vista.setLetraAleatoria(info['letra'])

        # Actualizar categorías
        inputs_categorias = self.vista.obtener_categorias()
        for categoria_text, input_widget in zip(categorias, inputs_categorias):
            input_widget.setText(categoria_text)

    def finalizar_ronda(self):
        """Acción al presionar STOP!"""
        # Recolectar respuestas y enviarlas al gestor
        respuestas = [input_widget.text() for input_widget in self.vista.obtener_categorias()]
        self.gestor_cliente.enviar_respuestas(respuestas)

        # Navegar a la siguiente vista usando el controlador de navegación
        # Por ahora suponemos que es la vista de resultados o siguiente ronda
        self.navegacion.mostrar("resultados")  # Este método debería existir en ControladorNavegacion
   