# sala_view.py
from PyQt6.QtWidgets import QWidget
#from sala_view_ui import Ui_SalaView
#from ronda_view_ui import Ui_MainWindow
from PyQt6 import QtCore, QtGui, QtWidgets

from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,QMessageBox
from PyQt6.QtGui import QFont
from PyQt6 import QtCore
from PyQt6.QtGui import QValidator

class PrimeraLetraValidator(QValidator):
    def __init__(self, letra, parent=None):
        super().__init__(parent)
        self.letra = letra.lower()

    def validate(self, texto, pos):
        if texto == "":
            return (QValidator.State.Intermediate, texto, pos)
        if texto.lower().startswith(self.letra):
            return (QValidator.State.Acceptable, texto, pos)
        return (QValidator.State.Invalid, texto, pos)

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
        self.label.setGeometry(QtCore.QRect(40, 0, 200, 121))
        font = QFont("Verdana", 40, QFont.Weight.Bold)
        self.label.setFont(font)
        header_layout.addWidget(self.label)

        # Número de ronda
        self.nroronda_label = QLabel("1/3")
        self.nroronda_label.setGeometry(QtCore.QRect(250, 0, 150, 121))  # Ajusté la posición
        font_ronda = QFont("Verdana", 40, QFont.Weight.Bold)
        self.nroronda_label.setFont(font_ronda)
        font_ronda.setPointSize(40)  # Reducido el tamaño de la fuente a 35
        header_layout.addWidget(self.nroronda_label)

        # Letra aleatoria
        self.lettra_texto_label = QLabel("Letra:")
        self.lettra_texto_label.setGeometry(QtCore.QRect(750, 0, 190, 121))  # Posicionada junto a la ronda
        font_letra_text = QFont("Verdana", 40, QFont.Weight.Bold)
        self.lettra_texto_label.setFont(font_letra_text)
        header_layout.addWidget(self.lettra_texto_label)

        self.letra_label = QLabel("R")
        self.letra_label.setGeometry(QtCore.QRect(940, 0, 80, 121))  # Posicionada junto a "Letra:"
        font_letra = QFont("Verdana", 40, QFont.Weight.Bold)
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

        for line_edit in self.inputs:
            line_edit.setMinimumHeight(55)
            line_edit.setFont(QFont("Verdana", 16))
            line_edit.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border: 1px solid #4CAF50;
                }
            """)

        # --- Botón STOP! ---
        self.enviar_respuestas_btn = QPushButton("STOP!", parent=self)
        self.enviar_respuestas_btn.setFont(QFont("Verdana", 26, QFont.Weight.Bold))
        self.enviar_respuestas_btn.setMinimumSize(320, 85)
        self.enviar_respuestas_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(self.enviar_respuestas_btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.enviar_respuestas_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: 4px solid #b71c1c;
                border-radius: 18px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #f44336;
                border: 4px solid #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
                padding-top: 14px;
                padding-bottom: 10px;
            }
        """)

    # --- Métodos de acceso / actualización ---
    def obtener_categorias_input(self):
        """Devuelve la lista de QLineEdit de las categorías"""
        return self.inputs

    def obtener_categorias_label(self):
        """Devuelve la lista de QLabel de las categorías"""
        return self.labels_categorias

    def set_numero_ronda(self, ronda, totalRondas):
        self.nroronda_label.setText(f"{ronda}/{totalRondas}")

    # def setLetraAleatoria(self, letra):
    #     self.letra_label.setText(letra)
    
    def setLetraAleatoria(self, letra):
            self.letra_label.setText(letra)
            self.agregar_validadores(letra)

    def agregar_validadores(self, letra):
        for input in self.inputs:
            input.setValidator(PrimeraLetraValidator(f"{letra}", input))
            input.setPlaceholderText(f"{letra}...")


    def aviso_completar_categorias(self, nombre):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Advertencia")
        msg.setText(f"Respuestas incompletas {nombre}. Debes completar todas las categorías antes de presionar STOP.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()