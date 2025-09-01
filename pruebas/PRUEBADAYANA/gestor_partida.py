import Pyro5.api
import threading
import time
from partida import Partida
from strategies import PuntajeSimple

@Pyro5.api.expose
class GestorPartida:
    def __init__(self, max_jugadores=3, strategy=None):
        self.partida = Partida()
        self.max_jugadores = max_jugadores
        self.lock = threading.Lock()
        self.strategy = strategy if strategy else PuntajeSimple()

    def check_nickname(self, nickname):
        return self.partida.is_nickname_disponible(nickname)

    def registrar_cliente(self, nickname, nombre_logico):
        proxy_cliente = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico}")
        with self.lock:
            self.partida.agregar_jugador_partida(nickname, proxy_cliente)
            info = self.partida.get_info_partida_json()
            proxy_cliente.recibir_info_sala(info)
            if len(self.partida.jugadores) >= self.max_jugadores:
                threading.Thread(target=self.iniciar_ronda).start()

    def iniciar_ronda(self):
        for ronda in range(self.partida.rondas):
            letra = self.partida.obtener_letra_aleatoria()
            info_ronda = self.partida.get_info_ronda_json(letra, ronda+1)
            print(f"[Servidor] Iniciando Ronda {ronda+1} con letra '{letra}'")
            self.partida.notificar_inicio_ronda(info_ronda)
            # Temporizador real 180 seg
            for i in range(180, 0, -1):
                print(f"⏱ Ronda {ronda+1} | Tiempo restante: {i}s", end="\r")
                time.sleep(1)
            # Aplicar Strategy a respuestas recibidas
            puntajes = self.strategy.calcular_puntaje(self.partida.respuestas_ronda)
            self.partida.notificar_fin_ronda(puntajes)
            self.partida.respuestas_ronda.clear()

    def enviar_respuestas(self, nickname, respuestas):
        with self.lock:
            self.partida.recibir_respuestas_jugador(nickname, respuestas)
