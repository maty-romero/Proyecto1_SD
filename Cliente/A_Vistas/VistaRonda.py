# sala_view.py
from PyQt6.QtWidgets import QWidget
#from sala_view_ui import Ui_SalaView
#from ronda_view_ui import Ui_MainWindow
from PyQt6 import QtCore, QtGui, QtWidgets

from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6 import QtCore

class VistaRonda(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1080, 720)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # --- Header: Ronda y Letra ---
        header_layout = QHBoxLayout()
        main_layout.addLayout(header_layout)

        # Label "Ronda"
        self.label = QLabel("Ronda")
        font = QFont("Verdana", 50, QFont.Weight.Bold)
        self.label.setFont(font)
        header_layout.addWidget(self.label)

        # Número de ronda
        self.nroronda_label = QLabel("1/3")
        font_ronda = QFont("Verdana", 30, QFont.Weight.Bold)
        self.nroronda_label.setFont(font_ronda)
        header_layout.addWidget(self.nroronda_label)

        # Letra aleatoria
        self.lettra_texto_label = QLabel("Letra:")
        font_letra_text = QFont("Verdana", 20, QFont.Weight.Bold)
        self.lettra_texto_label.setFont(font_letra_text)
        header_layout.addWidget(self.lettra_texto_label)

        self.letra_label = QLabel("R")
        font_letra = QFont("Verdana", 50, QFont.Weight.Bold)
        self.letra_label.setFont(font_letra)
        header_layout.addWidget(self.letra_label)

        header_layout.addStretch()

        # --- Categorías ---
        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)
        self.inputs = []
        self.labels_categorias = []

        for i in range(5):
            label = QLabel(f"<Categoria{i+1}>")
            label.setFont(QFont("Verdana", 20))
            self.labels_categorias.append(label)
            grid_layout.addWidget(label, i, 0)

            line_edit = QLineEdit()
            self.inputs.append(line_edit)
            grid_layout.addWidget(line_edit, i, 1)

        # --- Botón STOP! ---
        self.enviar_respuestas_btn = QPushButton("STOP!")
        self.enviar_respuestas_btn.setFont(QFont("Verdana", 14, QFont.Weight.Bold))
        main_layout.addWidget(self.enviar_respuestas_btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

    # --- Métodos de acceso / actualización ---
    def obtener_categorias(self):
        """Devuelve la lista de QLineEdit de las categorías"""
        return self.inputs

    def set_numero_ronda(self, ronda, totalRondas):
        self.nroronda_label.setText(f"{ronda}/{totalRondas}")

    def setLetraAleatoria(self, letra):
        self.letra_label.setText(letra)
