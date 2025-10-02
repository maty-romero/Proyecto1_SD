from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt

class VistaResultados(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Fondo de la ventana
        self.setStyleSheet("background-color: #f5f7fa;")

        # Layout principal para el scroll
        main_container = QVBoxLayout()
        main_container.setContentsMargins(0, 0, 0, 0)
        main_container.setSpacing(0)
        self.setLayout(main_container)

        # Crear un widget contenedor para el contenido
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f7fa;")
        
        # Crear el scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f7fa;
            }
            QScrollBar:vertical {
                border: none;
                background: #ecf0f1;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        main_container.addWidget(scroll_area)

        # Layout del contenido scrolleable
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # --- Título Principal ---
        titulo = QLabel("🎮 Resultados Finales")
        titulo.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(titulo)

        # --- Contenedor de Puntajes (Card) ---
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(15)

        # Título de puntajes
        titulo_puntajes = QLabel("📊 Tabla de Puntajes")
        titulo_puntajes.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        titulo_puntajes.setStyleSheet("color: #34495e;")
        titulo_puntajes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(titulo_puntajes)

        # Label de puntajes
        self.labelPuntajesTotales = QLabel("")
        self.labelPuntajesTotales.setFont(QFont("Segoe UI", 18))
        self.labelPuntajesTotales.setStyleSheet("""
            color: #2c3e50;
            padding: 15px;
            line-height: 1.6;
        """)
        self.labelPuntajesTotales.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelPuntajesTotales.setWordWrap(True)
        self.labelPuntajesTotales.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card_layout.addWidget(self.labelPuntajesTotales)

        main_layout.addWidget(card_frame)

        # --- Ganador (Destacado) ---
        ganador_frame = QFrame()
        ganador_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #ffd700, stop:0.5 #ffed4e, stop:1 #ffd700);
                border-radius: 15px;
                border: 3px solid #f39c12;
            }
        """)
        ganador_layout = QVBoxLayout(ganador_frame)
        ganador_layout.setContentsMargins(30, 25, 30, 25)
        
        self.labelGanador = QLabel("")
        self.labelGanador.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.labelGanador.setStyleSheet("color: #8b4513; background: transparent;")
        self.labelGanador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelGanador.setWordWrap(True)
        ganador_layout.addWidget(self.labelGanador)
        
        main_layout.addWidget(ganador_frame)

        # Espaciador
        main_layout.addStretch()

        # --- Botón Volver al Inicio ---
        self.botonVolverInicio = QPushButton("🏠 Volver al Inicio")
        self.botonVolverInicio.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.botonVolverInicio.setMinimumSize(280, 70)
        self.botonVolverInicio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.botonVolverInicio.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2980b9, stop:1 #21618c);
            }
        """)
        main_layout.addWidget(self.botonVolverInicio, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Guardar datos para procesamiento
        self.jugadores = []
        self.puntajes = {}

    def set_jugadores(self, jugadores: list[str]):
        self.jugadores = jugadores

    def set_puntajes_totales(self, puntajes: dict):
        self.puntajes = puntajes
        
        # Ordenar puntajes de mayor a menor
        puntajes_ordenados = sorted(puntajes.items(), key=lambda x: x[1], reverse=True)
        
        # Crear texto con medallas para los primeros 3 lugares
        lineas = []
        medallas = ["🥇", "🥈", "🥉"]
        
        for i, (nick, puntaje) in enumerate(puntajes_ordenados):
            if i < len(medallas):
                lineas.append(f"{medallas[i]} {nick}: {puntaje} pts")
            else:
                lineas.append(f"    {nick}: {puntaje} pts")
        
        texto = "\n".join(lineas)
        self.labelPuntajesTotales.setText(f"Puntajes Totales:\n{texto}")

    def set_ganador(self, ganador: str):
        self.labelGanador.setText(f"👑 Ganador de la partida: {ganador} 👑")