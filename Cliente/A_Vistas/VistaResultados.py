from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt

class VistaResultados(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # --- Header: Jugadores y Puntajes ---
        header_layout = QHBoxLayout()
        self.labelJugadores = QLabel("Jugadores: ")
        self.labelJugadores.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.labelJugadores.setStyleSheet("color: #0055ff;")
        self.labelJugadores.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.labelPuntajesTotales = QLabel("Puntajes Totales: ")
        self.labelPuntajesTotales.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.labelPuntajesTotales.setStyleSheet("color: green;")
        self.labelPuntajesTotales.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.labelPuntajesTotales.setWordWrap(True)

        header_layout.addWidget(self.labelJugadores)
        header_layout.addWidget(self.labelPuntajesTotales)
        main_layout.addLayout(header_layout)

        # --- Ganador ---
        self.labelGanador = QLabel("Ganador de la partida: ")
        self.labelGanador.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.labelGanador.setStyleSheet("color: orange;")
        self.labelGanador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.labelGanador)

        # --- Botón Volver al Inicio ---
        self.botonVolverInicio = QPushButton("Volver al Inicio")
        self.botonVolverInicio.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.botonVolverInicio.setStyleSheet("background-color: #0055ff; color: white; padding: 10px;")
        main_layout.addWidget(self.botonVolverInicio, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_jugadores(self, jugadores: list[str]):
        self.labelJugadores.setText("Jugadores: " + ", ".join(jugadores))

    def set_puntajes_totales(self, puntajes: dict):
        texto = "\n".join([f"  {nick}: {puntaje}" for nick, puntaje in puntajes.items()])
        self.labelPuntajesTotales.setText(f"Puntajes Totales:\n{texto}")

    def set_ganador(self, ganador: str):
        self.labelGanador.setText(f"Ganador de la partida: {ganador}")
