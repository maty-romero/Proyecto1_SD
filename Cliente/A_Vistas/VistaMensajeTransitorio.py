from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget

from PyQt6.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout
from PyQt6 import QtCore, QtGui

class VistaMensajeTransitorio(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.mensaje_label = QLabel("Mensaje de estado", self)
        fuente = QtGui.QFont("Verdana", 20, QtGui.QFont.Weight.Bold)
        fuente.setItalic(True)
        self.mensaje_label.setFont(fuente)
        self.mensaje_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.mensaje_label)

        # Botones de acción
        # botones_layout = QHBoxLayout()
        # self.boton_si = QPushButton("Sí")
        # self.boton_no = QPushButton("No")
        # botones_layout.addWidget(self.boton_si)
        # botones_layout.addWidget(self.boton_no)
        # layout.addLayout(botones_layout)

    def setMensaje(self, texto: str):
        self.mensaje_label.setText(texto)
        
    
