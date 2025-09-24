class Dispatcher:
    def __init__(self):
        self.servicios = {}
        # Registrado en Nodo Servidor
        #self.Dispatcher.registrar_servicio("comunicacion", self.ServComms)
        #self.Dispatcher.registrar_servicio("juego", self.ServJuego)
        #self.Dispatcher.registrar_servicio("db", self.ServDB)

    def registrar_servicio(self, nombre, servicio):
        self.servicios[nombre] = servicio

    def manejar_llamada(self, nombre_servicio: str, nombre_metodo: str, *args, **kwargs):
        servicio = self.servicios.get(nombre_servicio)
        if not servicio:
            raise ValueError(f"Servicio {nombre_servicio} no encontrado")
        metodo = getattr(servicio, nombre_metodo, None)
        if not metodo:
            raise ValueError(f"Método {nombre_metodo} no existe en {nombre_servicio}")
        print("Desde DISPACHER! Estoy por ejecutar el método respuestas_memoria_clientes_ronda")
        return metodo(*args, **kwargs)