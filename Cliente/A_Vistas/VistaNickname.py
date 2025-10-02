from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget

from PyQt6.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout, QMessageBox, QLineEdit
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
        #self.textEdit = QTextEdit()
        self.textEdit = QLineEdit()
        self.textEdit.setFixedHeight(40)
        #self.textEdit.setValidator(QIntValidator())  # Solo acepta números enteros (Es necesario?)
        self.textEdit.setPlaceholderText("Ingrese su nickname")  # Texto gris inicial
        layout.addWidget(self.textEdit)

        # Botón Ingresar
        self.btnIngresar = QPushButton("Ingresar")
        self.btnIngresar.setFixedSize(130, 40)
        layout.addWidget(self.btnIngresar, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        #Hace que al apretar enter el en QLine, accione el efecto de clickear el boton
        self.textEdit.returnPressed.connect(self.btnIngresar.click)
        
        # Estilos de la vista
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                font-family: Segoe UI;
                font-size: 16px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLabel {
                color: #333;
                font-size: 30px;
                font-weight: bold;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                background: white;
            }
        """)

    # Métodos de acceso (para el controlador)
    def getIngresarbtn(self):
        return self.btnIngresar

    def getNickname(self):
        return self.textEdit.text()

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
        msg.setText(f"El jugador {nombre} se ha unido a la sala correctamente.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
