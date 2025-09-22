from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget

from PyQt6.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt6 import QtCore, QtGui

class VistaNickname(QWidget):
    def __init__(self):
        super().__init__()

        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(layout)

        # Label
        self.label = QLabel("INGRESE SU NICKNAME PARA LA PARTIDA")
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # TextEdit para el nickname
        self.textEdit = QTextEdit()
        self.textEdit.setFixedHeight(30)
        layout.addWidget(self.textEdit)

        # Botón Ingresar
        self.btnIngresar = QPushButton("Ingresar")
        self.btnIngresar.setFixedWidth(120)
        layout.addWidget(self.btnIngresar, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

    # Métodos de acceso (para el controlador)
    def getIngresarbtn(self):
        return self.btnIngresar

    def getNickname(self):
        return self.textEdit.toPlainText()

    # Mensajes
    def aviso_nickName_repetido(self, nombre):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Advertencia")
        msg.setText(f"El nombre {nombre} ya existe! Ingrese otro.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def aviso_nickName_exitoso(self, nombre):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("¡Éxito!")
        msg.setText(f"El nickname {nombre} se ha unido a la sala correctamente.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
