class Dispatcher:
    def __init__(self):
        self.servicios = {}
    def registrar_servicio(self, nombre, servicio):
        self.servicios[nombre] = servicio

    def manejar_llamada(self, nombre_servicio: str, nombre_metodo: str, *args, **kwargs):
        servicio = self.servicios.get(nombre_servicio)
        if not servicio:
            raise ValueError(f"Servicio {nombre_servicio} no encontrado")
        metodo = getattr(servicio, nombre_metodo, None)
        if not metodo:
            raise ValueError(f"Método {nombre_metodo} no existe en {nombre_servicio}")
        return metodo(*args, **kwargs)