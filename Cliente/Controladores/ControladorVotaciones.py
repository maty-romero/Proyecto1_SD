class ControladorVotaciones:
    def __init__(self, vista: 'VistaVotaciones', gestor_cliente):
        self.vista = vista
        self.navegacion = None
        self.gestor_cliente = gestor_cliente
        #self.partida = gestor_cliente.partida

        #self.vista.get_boton_confirmar_voto().clicked.connect(self.ver_puntajes_ronda)
        #self.actualizar_vista_votaciones()

    def setNavegacion(self, controlador_navegacion):
        self.navegacion = controlador_navegacion

    def mostrar_info_votaciones(self):
        respuestas_mock = {
            "Objeto con T": [(f"Jugador{i}", f"Objeto{i}") for i in range(1, 10)],
            "Animal con T": [(f"Jugador{i}", f"Animal{i}") for i in range(1, 10)],
            "Comida con T": [(f"Jugador{i}", f"Comida{i}") for i in range(1, 10)],
        }

        self.vista.set_ronda_y_letra(2, 5, "T")
        self.vista.agregar_respuestas_para_votar(respuestas_mock)
        #pass

    def actualizar_vista_votaciones(self):
        # Datos ficticios para testeo
        # Simular datos de prueba
        pass

        # Actualizar encabezado
        #self.vista.set_ronda_y_letra(ronda_actual, total_rondas, letra)

        # Poblar categorías con jugadores
        #self.vista.agregar_categorias(categorias, jugadores)
        """
        ronda_actual = self.partida.get_ronda_actual()
        total_rondas = self.partida.get_nro_ronda()
        letra = self.partida.get_letra_random()
        self.vista.set_ronda_y_letra(ronda_actual, total_rondas, letra)

        categorias = self.partida.get_categorias()
        jugadores = self.gestor_cliente.obtener_nicknames_jugadores()
        self.vista.agregar_categorias(categorias, jugadores)
        """

    def ver_puntajes_ronda(self):
        self.navegacion.mostrar("resultados")  # o lo que corresponda
