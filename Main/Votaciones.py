from Partida.py import Partida
ytp.aditr
respuestasDict = {
    "Frutas": {"Fiorella": "Alacrán", "Dayana": "Ananá", "PEPE": "Arándanos", "Mari": "Ananá"},
    "Animales": {"Fiorella": "Avestruz", "Dayana": "Araña", "PEPE": "Amarillo", "Mari": "A"}
}


for categoria, jugadores in respuestasDict.items():
    print(f"--- Respuestas para la categoría: {categoria} ---")
    for jugador, respuesta in jugadores.items():
        print(f"  {jugador}: {respuesta}")


class Votaciones:
    def __init__(self, partida:Partida):
        self.partida=partida# La instancia de la partida para acceder a jugadores y respuestas
        self.votaciosnes={} # Diccionario de votaciones por categoría