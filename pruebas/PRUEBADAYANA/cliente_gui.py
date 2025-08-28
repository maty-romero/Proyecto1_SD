import sys, threading, json
import Pyro5.api
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFormLayout

@Pyro5.api.expose
class ClienteGUI:
    def __init__(self, nickname):
        self.nickname = nickname
        self.app = QApplication(sys.argv)
        self.win = QWidget()
        self.win.setWindowTitle(f"Jugador: {nickname}")
        self.layout = QVBoxLayout()
        self.info_sala = QTextEdit()
        self.info_sala.setReadOnly(True)
        self.form_layout = QFormLayout()
        self.inputs = {}
        self.enviar_btn = QPushButton("Enviar Respuestas")
        self.layout.addWidget(QLabel(f"Jugador: {nickname}"))
        self.layout.addWidget(self.info_sala)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.enviar_btn)
        self.win.setLayout(self.layout)
        self.win.show()
        self.enviar_btn.clicked.connect(self.enviar_respuestas)
        self.juego_proxy = None

    def conectar_servidor(self):
        self.juego_proxy = Pyro5.api.Proxy("PYRONAME:gestor.partida")
        ip_local = "127.0.0.1"
        daemon = Pyro5.api.Daemon(host=ip_local)
        uri = daemon.register(self, objectId=f"jugador.{self.nickname}")
        ns = Pyro5.api.locate_ns()
        ns.register(f"jugador.{self.nickname}", uri)
        self.juego_proxy.registrar_cliente(self.nickname, f"jugador.{self.nickname}")
        threading.Thread(target=daemon.requestLoop, daemon=True).start()

    def recibir_info_sala(self, info):
        self.info_sala.append(f"🟢 Info Sala:\n{info}\n")

    def recibir_info_inicio_ronda(self, info):
        self.info_sala.append(f"🟡 Inicio Ronda:\n{info}\n")
        info_json = json.loads(info)
        # Limpiar formulario y crear inputs por categoría
        for cat in info_json["categorias"]:
            if cat not in self.inputs:
                self.inputs[cat] = QLineEdit()
                self.form_layout.addRow(QLabel(cat), self.inputs[cat])

    def recibir_info_fin_ronda(self, resultados):
        self.info_sala.append(f"🔵 Puntajes Ronda:\n{resultados}\n")

    def enviar_respuestas(self):
        respuestas = {cat: self.inputs[cat].text() for cat in self.inputs}
        self.juego_proxy.enviar_respuestas(self.nickname, respuestas)
        self.info_sala.append("✅ Respuestas enviadas!")
        # Limpiar formulario
        for inp in self.inputs.values():
            inp.clear()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    nickname = input("Ingrese su NickName: ")
    cliente = ClienteGUI(nickname)
    cliente.conectar_servidor()
    cliente.run()
