import json 
from types import SimpleNamespace


"""
def json_to_object(json_string: str):
    object_info = json.loads(json_string, object_hook=lambda d: SimpleNamespace(**d))
    return object_info
"""

#def 

def main():
    info_ronda_json = '{"letra": "M", "categorias": ["Nombres", "Paises o ciudades", "Objetos"], "nroRonda": 3}'

    infoRonda = json.loads(info_ronda_json, object_hook=lambda d: SimpleNamespace(**d))
    print(f"Cliente Jugando Ronda: {infoRonda.nroRonda}")
    print(f"Letra Ronda: {infoRonda.letra}. Comienza la ronda!")

    respuestasDict = {clave: "" for clave in infoRonda.categorias}

    for clave in respuestasDict:
        respuesta = input(f"Ingrese respuesta para {clave}: ")
        # Validacion primer letra 
        while respuesta[0] != infoRonda.letra: 
            print(f"Estamos jugando con la letra {infoRonda.letra}!")
            respuesta = input(f"Ingrese respuesta para {clave}: ")
            
        respuestasDict[clave] = respuesta

    json_respuestas = json.dumps(respuestasDict) # JSON
    print(f"La respuestas del cliente son: {json_respuestas}")

    

    """
    {'Nombres': 'Martin', 'Paises o ciudades': 'Manwatwa', 'Objetos': 'Mar'}
    """

    #cliente.EnviarRespuestas(respuestasJson)
if __name__ == "__main__":
    main()