from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt


#esto a lo ultimo como pendiente
class VistaPuntajes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        # --- Header: Ronda y Letra ---
        header_layout = QHBoxLayout()
        self.labelRondaConNumero = QLabel("Ronda: 1/3")
        self.labelRondaConNumero.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.labelLetraRandom = QLabel("Letra: T")
        self.labelLetraRandom.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))

        # Label para mostrar los puntajes de todos los jugadores
        self.labelPuntajes = QLabel("")
        self.labelPuntajes.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.labelPuntajes.setStyleSheet("color: green;")
        self.labelPuntajes.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(self.labelRondaConNumero)
        header_layout.addWidget(self.labelLetraRandom)
        header_layout.addWidget(self.labelPuntajes, stretch=1)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # --- Scroll de resultados por categoría ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.scroll_area)

        # Contenedor raíz dentro del scroll
        outer_container = QWidget()
        outer_layout = QHBoxLayout(outer_container)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.scroll_area.setWidget(outer_container)

        # Contenedor de categorías
        self.scroll_content = QWidget()
        self.scroll_content.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.scroll_content)

    def set_ronda_y_letra(self, ronda_actual: int, total_rondas: int, letra: str):
        self.labelRondaConNumero.setText(f"Ronda: {ronda_actual}/{total_rondas}")
        self.labelLetraRandom.setText(f"Letra: {letra}")

    def set_puntajes(self, puntajes: dict):
        # puntajes = {"jugador1": 10, "jugador2": 8, ...}
        texto = " | ".join([f"{nick}: {puntaje}" for nick, puntaje in puntajes.items()])
        self.labelPuntajes.setText(texto)

    def _limpiar_scroll(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def agregar_resultados_por_categoria(self, resultados_por_categoria: dict[str, list[tuple[str, str, int]]]):
        """
        resultados_por_categoria = {
            "Nombres con T": [("jugador1", "respuesta1", 2), ("jugador2", "respuesta2", 1)],
            ...
        }
        """
        self._limpiar_scroll()

        fuente_subtitulo = QFont("Segoe UI", 18, QFont.Weight.Bold)
        fuente_items = QFont("Segoe UI", 16)

        for categoria, resultados in resultados_por_categoria.items():
            subtitulo = QLabel(categoria)
            subtitulo.setFont(fuente_subtitulo)
            subtitulo.setStyleSheet("color: rgb(0, 85, 255);")
            subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(subtitulo)

            for nickname, respuesta, puntaje in resultados:
                fila_widget = QWidget()
                fila_layout = QHBoxLayout(fila_widget)
                fila_layout.setContentsMargins(20, 5, 20, 5)
                fila_layout.setSpacing(30)

                label_nick = QLabel(nickname)
                label_nick.setFont(fuente_items)
                label_nick.setFixedWidth(200)
                label_nick.setAlignment(Qt.AlignmentFlag.AlignCenter)

                label_resp = QLabel(respuesta)
                label_resp.setFont(fuente_items)
                label_resp.setFixedWidth(400)
                label_resp.setWordWrap(True)
                label_resp.setAlignment(Qt.AlignmentFlag.AlignCenter)

                label_puntaje = QLabel(f"Puntaje: {puntaje}")
                label_puntaje.setFont(fuente_items)
                label_puntaje.setStyleSheet("color: green;")
                label_puntaje.setAlignment(Qt.AlignmentFlag.AlignCenter)

                fila_layout.addWidget(label_nick)
                fila_layout.addWidget(label_resp)
                fila_layout.addWidget(label_puntaje)
                fila_layout.addStretch()

                self.scroll_layout.addWidget(fila_widget)

        self.scroll_layout.addStretch()
        
