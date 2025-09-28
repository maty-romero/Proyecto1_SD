from PyQt6.QtWidgets import QWidget, QLabel, QPushButton
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt # Para Qt.CursorShape

class VistaSala(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Sala de Juego - TuttiFrutti")
        font_title = QtGui.QFont("Verdana", 44, QtGui.QFont.Weight.Bold)
        font_label = QtGui.QFont("Verdana", 14, QtGui.QFont.Weight.Bold)
        font_label2 = QtGui.QFont("Verdana", 14, QtGui.QFont.Weight.Normal)

        # Título
        self.label = QLabel("TUTIFRUTTI", parent=self)
        self.label.setGeometry(QtCore.QRect(280, 20, 520, 100))
        self.label.setFont(font_title)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Botón "Estoy listo"
        self.confirmar_jugador_btn = QPushButton("Estoy Listo!", parent=self)
        self.confirmar_jugador_btn.setGeometry(QtCore.QRect(410, 600, 260, 60))
        self.confirmar_jugador_btn.setFont(QtGui.QFont("Verdana", 14, QtGui.QFont.Weight.Bold))
        self.confirmar_jugador_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Labels de información
        self.label1 = QLabel("Jugador:", parent=self)
        self.label1.setGeometry(QtCore.QRect(60, 140, 200, 50))
        self.label1.setFont(font_label)

        self.nickname_label = QLabel("<Pepe>", parent=self)
        self.nickname_label.setGeometry(QtCore.QRect(200, 140, 300, 50))
        self.nickname_label.setFont(font_label2)
        #self.nickname_label.setStyleSheet("color: #0066cc;")

        self.label1_2 = QLabel("Rondas a Jugar:", parent=self)
        self.label1_2.setGeometry(QtCore.QRect(680, 140, 220, 50))
        self.label1_2.setFont(font_label)

        self.nrorondas_label = QLabel("<3>", parent=self)
        self.nrorondas_label.setGeometry(QtCore.QRect(910, 140, 80, 50))
        self.nrorondas_label.setFont(font_label2)
        #self.nrorondas_label.setStyleSheet("color: #0066cc;")

        self.label1_3 = QLabel("Categorias:", parent=self)
        self.label1_3.setGeometry(QtCore.QRect(60, 240, 200, 50))
        self.label1_3.setFont(font_label)

        self.categorias_label = QLabel("<Listado_Categorias>", parent=self)
        self.categorias_label.setGeometry(QtCore.QRect(200, 240, 600, 50))
        self.categorias_label.setFont(QtGui.QFont("Verdana", 12, QtGui.QFont.Weight.Normal))
        #self.categorias_label.setStyleSheet("color: #800080;")

        self.label1_5 = QLabel("Jugadores en Sala:", parent=self)
        self.label1_5.setGeometry(QtCore.QRect(60, 340, 220, 50))
        self.label1_5.setFont(font_label)

        self.jugadores_label = QLabel("<Listado_Jugadores>", parent=self)
        self.jugadores_label.setGeometry(QtCore.QRect(280, 340, 400, 50))
        self.jugadores_label.setFont(font_label2)
        #self.jugadores_label.setStyleSheet("color: #cc3300;")
        
        # Label para el dato de "Jugadores Requeridos"
        
        self.label1_4 = QLabel("Jugadores Requeridos:", parent=self)
        self.label1_4.setGeometry(QtCore.QRect(60, 440, 260, 50))
        self.label1_4.setFont(font_label)
        
        self.jugadores_requeridos_label = QLabel("<5>", parent=self)
        self.jugadores_requeridos_label.setGeometry(QtCore.QRect(320, 440, 100, 50))
        self.jugadores_requeridos_label.setFont(font_label2)
        #self.jugadores_requeridos_label.setStyleSheet("color: #0066cc;")

        self.estado_sala_label = QLabel("<Msg_Estado_Sala>", parent=self)
        self.estado_sala_label.setGeometry(QtCore.QRect(0, 500, 1080, 80))
        estado_font = QtGui.QFont("Verdana", 14, QtGui.QFont.Weight.Bold)
        estado_font.setItalic(True)
        self.estado_sala_label.setFont(estado_font)
        self.estado_sala_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.estado_sala_label.setStyleSheet("color: #990000;")
        
        self.setStyleSheet("""
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    # Métodos de acceso/modificación
    def setNombreJugador(self, nombre):
        self.nickname_label.setText(nombre)

    def getNombreJugador(self):
        return self.nickname_label.text()

    def setRonda(self, cantRondas):
        self.nrorondas_label.setText(str(cantRondas))

    def setListaCategoria(self, categorias):
        self.categorias_label.setText(categorias)

    def setEstadoSala(self, estadoSala):
        self.estado_sala_label.setText(estadoSala)

    def setListaJugadores(self, jugadores):
        self.jugadores_label.setText(jugadores)

    def getUnirSala(self):
        return self.confirmar_jugador_btn
    
    def setJugadoresRequeridos(self,canti_jugadores):
        return self.jugadores_requeridos_label.setText(canti_jugadores)