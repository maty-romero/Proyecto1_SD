from PyQt6 import QtWidgets
from vistas.Votaciones import Ui_MainWindow
from controlador.ControladorPuntajes import ControladorPuntajes 
from Partida import Partida 

class ControladorVotaciones:

    def __init__(self):
        # Inicializa la ventana principal
        self.MainWindow = QtWidgets.QMainWindow()
        self.vista = Ui_MainWindow()
        self.vista.setupUi(self.MainWindow)
        
        self.partida = Partida()  # Crea una nueva partida
        
        ## pasamos la instancia de partida al controlador de puntajes
        self.controlador_puntajes = ControladorPuntajes(self.partida)  # Se pasa la instancia de partida
        
        # Actualizar vista con la información de la ronda y la letra
        self.actualizar_vista_ronda()
        # Conectar botones a eventos
        self.vista.get_boton_confirmar_voto().clicked.connect(self.verPuntajesRonda)
        self.MainWindow.show()
        
    def verPuntajesRonda(self):
        # Recoger las respuestas y los estados de los checkboxes
        #respuestas, checkboxes = self.obtener_respuestas_checkboxes()
        # Calcular puntajes
        # puntajes = self.calcular_puntajes(respuestas, checkboxes)

        # Cerrar la ventana actual (votaciones)
        self.MainWindow.close()
        # Crear y mostrar la ventana de puntajes
        self.controlador_puntajes = ControladorPuntajes()
    
        # self.controlador_puntajes.MainWindow.show()
        
    def actualizar_vista_ronda(self):
        # Obtener la ronda y la letra
        numero_ronda = self.partida.get_nro_ronda()
        numero_ronda_actual=self.partida.get_ronda_actual()
        letra = self.partida.get_letra_random()

        # Actualizar las etiquetas de la vista con el número de ronda y la letra
        self.vista.labelRondaConNumero.setText(f"Ronda: {numero_ronda_actual}/{numero_ronda}")
        self.vista.labelLetraRandom.setText(f"Letra: {letra}")
    
    # def obtener_respuestas_checkboxes(self):
    #     """
    #     Recoge las respuestas y el estado de los checkboxes para validarlas.
    #     """
    #     respuestas = {}
    #     checkboxes = {}

    #     categorias = ["Animal con T", "Color con T", "Objeto con T", "Pais con T"]
    #     num_jugadores = 3  

    #     for categoria in categorias:
    #         respuestas[categoria] = {}
    #         checkboxes[categoria] = {}

    #         for i in range(num_jugadores):
    #             # Buscar las respuestas de los jugadores
    #             response_label = self.vista.scroll_area_widget_contents.findChild(QtWidgets.QLabel, f"respuesta_{categoria}_jugador_{i+1}")
    #             check_box = self.vista.scroll_area_widget_contents.findChild(QtWidgets.QCheckBox, f"checkbox_{categoria}_jugador_{i+1}")
                
    #             respuestas[categoria][f"jugador_{i+1}"] = response_label.text()  # Respuesta del jugador
    #             checkboxes[categoria][f"jugador_{i+1}"] = check_box.isChecked()  # Estado del checkbox

    #     return respuestas, checkboxes
    
    
    # def calcular_puntajes(self, respuestas, checkboxes):
    #     """
    #     Calcula los puntajes según las respuestas y el estado de los checkboxes.
    #     10 puntos: Respuesta única entre todos los jugadores.
    #     5 puntos: Respuesta repetida entre algunos jugadores.
    #     0 puntos: Respuesta inválida o no votada.
    #     """
    #     puntajes = {}

    #     # Procesar cada categoría
    #     for categoria, respuestas_categoria in respuestas.items():
    #         respuestas_unicas = {}
    #         respuestas_repetidas = {}
    #         puntajes_categoria = {}

    #         # Recorrer las respuestas y agruparlas
    #         for jugador, respuesta in respuestas_categoria.items():
    #             if respuesta not in respuestas_unicas:
    #                 respuestas_unicas[respuesta] = []
    #             respuestas_unicas[respuesta].append(jugador)

    #         # Asignar puntos
    #         for respuesta, jugadores in respuestas_unicas.items():
    #             if len(jugadores) == 1:
    #                 # Respuesta única
    #                 for jugador in jugadores:
    #                     puntajes_categoria[jugador] = 10
    #             elif len(jugadores) > 1:
    #                 # Respuesta repetida
    #                 for jugador in jugadores:
    #                     puntajes_categoria[jugador] = 5

    #         # Asignar 0 puntos a respuestas no válidas
    #         for jugador, respuesta in respuestas_categoria.items():
    #             if respuesta == "" or not checkboxes[categoria].get(jugador, False):
    #                 puntajes_categoria[jugador] = 0

    #         puntajes[categoria] = puntajes_categoria

    #     return puntajes
