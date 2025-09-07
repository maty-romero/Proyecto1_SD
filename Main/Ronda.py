from Respuesta import Respuesta

class Ronda:
    def __init__(self, nro_ronda, letra):
        self.__nro_ronda = nro_ronda
        self.__finalizada = False
        self.__letra_ronda = letra
        self.__dictRespuestas = {}

    def ingresa_respuesta(self,nickname,categoria,respuesta):
        if nickname not in self.__dictRespuestas:
            self.__dictRespuestas[nickname] = {}
        self.__dictRespuestas[nickname][categoria] = Respuesta(categoria, respuesta)
    
    def get_nro_ronda (self):
        return self.__nro_ronda
    
    def get_letra(self):
        return self.__letra_ronda
    
    def get_respuestas(self):
        return self.__dictRespuestas
    
    def finalizar_ronda(self):
        self.__finalizada = True
    
    def is_finalizada(self):
        return self.__finalizada
    
    def to_dict(self):
        return {
            "nro_ronda": self.__nro_ronda,
            "letra_ronda": self.__letra_ronda,
            "finalizada": self.__finalizada,
            "respuestas": {
                jugador: {
                    categoria: resp.to_dict()
                    for categoria, resp in categorias.items()
                }
                for jugador, categorias in self.__dictRespuestas.items()
            }
        }