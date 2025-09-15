class Dispatcher:
    def __init__(self):
        self.servicios = {}
        # self.ServComms = None
        # self.ServDB = None
        # self.ServJuego = None

    def registrar_servicio(self, nombre, servicio):
        self.servicios[nombre] = servicio

    def manejar_llamada(self, id_cliente, nombre_servicio, metodo, datos, **kwargs):

        servicio = self.servicios.get(nombre_servicio)

        if not servicio:
            raise ValueError(f"Servicio {nombre_servicio} no encontrado")

        metodo = getattr(servicio, nombre_servicio, None)
        if not metodo:
            raise ValueError(f"Método {nombre_servicio} no existe en {nombre_servicio}")

        return metodo(datos, **kwargs)