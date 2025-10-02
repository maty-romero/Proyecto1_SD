from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QCheckBox, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt


class VistaVotaciones(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkboxes_por_categoria = {}  # {categoria: [(nickname, checkbox), ...]}

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        # --- Header: Ronda y Letra ---
        header_layout = QHBoxLayout()
        self.labelRondaConNumero = QLabel("Ronda: -/-")
        self.labelRondaConNumero.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.labelLetraRandom = QLabel("Letra: -")
        self.labelLetraRandom.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))

        self.labelMensajeVotacion = QLabel("Esperando jugadores para la Votacion!!")
        self.labelMensajeVotacion.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.labelMensajeVotacion.setStyleSheet("color: orange;")
        self.labelMensajeVotacion.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(self.labelRondaConNumero)
        header_layout.addWidget(self.labelLetraRandom)
        header_layout.addWidget(self.labelMensajeVotacion, stretch=1)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # --- Scroll de categorías ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setStyleSheet("background-color: #f0f2f5; border: none;")
        main_layout.addWidget(self.scroll_area)

        # Contenedor de categorías
        self.scroll_content = QWidget()
        self.scroll_content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)

        self.setStyleSheet("""
            QWidget {
                font-family: Segoe UI;
            }
            QLabel {
                color: #222222;
            }
        """)

        self.scroll_area.setWidget(self.scroll_content)

    def set_ronda_y_letra(self, ronda_actual: int, total_rondas: int, letra: str):
        self.labelRondaConNumero.setText(f"Ronda: {ronda_actual}/{total_rondas}")
        self.labelLetraRandom.setText(f"Letra: {letra}")

    def set_mensaje_votacion(self, mensaje: str):
        self.labelMensajeVotacion.setText(mensaje)

    def limpiar_scroll(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def agregar_respuestas_para_votar(self, respuestas_por_categoria: dict[str, list[tuple[str, str]]]):
        self.limpiar_scroll()
        self.checkboxes_por_categoria = {}

        fuente_subtitulo = QFont("Segoe UI", 18, QFont.Weight.Bold)
        fuente_items = QFont("Segoe UI", 16)

        for categoria, respuestas in respuestas_por_categoria.items():
            # --- Caja estilo tarjeta ---
            categoria_box = QFrame()
            categoria_box.setStyleSheet("""
                QFrame {
                    border: 1px solid #dcdcdc;
                    border-radius: 12px;
                    background-color: #ffffff;
                }
            """)

            categoria_layout = QVBoxLayout(categoria_box)
            categoria_layout.setSpacing(10)
            categoria_layout.setContentsMargins(15, 15, 15, 15)

            # --- Título de categoría ---
            titulo = QLabel(categoria)
            titulo.setFont(fuente_subtitulo)
            titulo.setStyleSheet("color: #0055ff;")
            titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)   # ⬅ centrado
            categoria_layout.addWidget(titulo)

            self.checkboxes_por_categoria[categoria] = []

            for idx, (nickname, respuesta) in enumerate(respuestas):
                fila_widget = QWidget()
                fila_layout = QHBoxLayout(fila_widget)
                fila_layout.setContentsMargins(5, 5, 5, 5)
                fila_layout.setSpacing(20)

                label_nick = QLabel(nickname)
                label_nick.setFont(fuente_items)
                label_nick.setStyleSheet("color: #444; font-weight: 500;")
                label_nick.setFixedWidth(150)
                label_nick.setAlignment(Qt.AlignmentFlag.AlignCenter) 

                label_resp = QLabel(respuesta)
                label_resp.setFont(fuente_items)
                label_resp.setStyleSheet("color: #222;")
                label_resp.setWordWrap(True)
                label_resp.setFixedWidth(250)
                label_resp.setAlignment(Qt.AlignmentFlag.AlignCenter)

                checkbox_invalido = QCheckBox("Votar negativamente")
                checkbox_invalido.setFont(fuente_items)
                checkbox_invalido.setStyleSheet("color: #cc0000;")

                self.checkboxes_por_categoria[categoria].append((nickname, checkbox_invalido))

                fila_layout.addWidget(label_nick)
                fila_layout.addStretch()
                fila_layout.addWidget(label_resp)
                fila_layout.addStretch()
                fila_layout.addWidget(checkbox_invalido)

                categoria_layout.addWidget(fila_widget)

                # Línea divisoria entre filas (excepto la última)
                if idx < len(respuestas) - 1:
                    line = QFrame()
                    line.setFrameShape(QFrame.Shape.HLine)
                    line.setFrameShadow(QFrame.Shadow.Sunken)
                    categoria_layout.addWidget(line)

            self.scroll_layout.addWidget(categoria_box)

    def obtener_votos(self):
        """
        Devuelve un diccionario con los votos del usuario:
        {
            'nickname1': {'Nombres': True, 'Animales': False, ...},
            'nickname2': {...},
            ...
        }
        True = voto negativo (checkbox marcado), False = voto positivo (checkbox desmarcado)
        """
        votos = {}
        for categoria, lista in self.checkboxes_por_categoria.items():
            cat_simple = categoria.split(" con ")[0]
            for nickname, checkbox in lista:
                if nickname not in votos:
                    votos[nickname] = {}
                votos[nickname][cat_simple] = not checkbox.isChecked()

        return votos

    def reiniciar_labels(self):
        self.limpiar_scroll()
        self.labelRondaConNumero.setText("Ronda: -/-")
        self.labelLetraRandom.setText("Letra: -")
        self.labelMensajeVotacion.setText("Esperando jugadores para la Votacion!!")
        self.checkboxes_por_categoria = {}
