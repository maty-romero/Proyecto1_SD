class Respuesta:

    def __init__(self, categoria, respuesta):
        self.categoria = categoria
        self.respuesta = respuesta
        self.valido = True
        self.puntaje_asignado = 0
        self.votos = []

    def is_valid(self):
        return self.valido
    
    def get_puntaje(self):
        return self.puntaje_asignado
    
    def registrar_voto(self,voto:bool):
        self.votos.append(voto)

    def contar_votos(self):
        valido = 0
        no_valido = 0
        for voto in self.votos:
            if voto:
                valido =+ 1
            else:
                no_valido =+ 1
        
        if valido == no_valido or valido < no_valido:
            self.valido = False

    
    def to_dict(self):
        return {
            "categoria": self.categoria,
            "respuesta": self.respuesta,
            "valido": self.valido,
            "puntaje asignado": self.puntaje_asignado
        }