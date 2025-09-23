from PyQt6.QtWidgets import QWidget, QLabel, QPushButton
from PyQt6 import QtCore, QtGui

class VistaSala(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        font_title = QtGui.QFont("Verdana", 50, QtGui.QFont.Weight.Bold)
        font_label = QtGui.QFont("Verdana", 15, QtGui.QFont.Weight.Bold)

        # Título
        self.label = QLabel("TUTIFRUTTI", parent=self)
        self.label.setGeometry(QtCore.QRect(320, 20, 521, 121))
        self.label.setFont(font_title)

        # Botón "Estoy listo"
        self.confirmar_jugador_btn = QPushButton("Estoy Listo!", parent=self)
        self.confirmar_jugador_btn.setGeometry(QtCore.QRect(430, 620, 261, 61))
        self.confirmar_jugador_btn.setFont(QtGui.QFont("Verdana", 14, QtGui.QFont.Weight.Bold))

        # Labels de información
        self.label1 = QLabel("Jugador:", parent=self)
        self.label1.setGeometry(QtCore.QRect(60, 160, 241, 61))
        self.label1.setFont(font_label)

        self.nickname_label = QLabel("<Pepe>", parent=self)
        self.nickname_label.setGeometry(QtCore.QRect(190, 160, 300, 61))
        self.nickname_label.setFont(font_label)

        self.label1_2 = QLabel("Rondas a Jugar:", parent=self)
        self.label1_2.setGeometry(QtCore.QRect(700, 170, 241, 61))
        self.label1_2.setFont(font_label)

        self.nrorondas_label = QLabel("<3>", parent=self)
        self.nrorondas_label.setGeometry(QtCore.QRect(920, 170, 101, 61))
        self.nrorondas_label.setFont(font_label)

        self.label1_3 = QLabel("Categorias:", parent=self)
        self.label1_3.setGeometry(QtCore.QRect(50, 270, 241, 61))
        self.label1_3.setFont(font_label)

        self.categorias_label = QLabel("<Listado_Categorias>", parent=self)
        self.categorias_label.setGeometry(QtCore.QRect(220, 270, 600, 61))
        self.categorias_label.setFont(QtGui.QFont("Verdana", 12, QtGui.QFont.Weight.Bold))

        self.label1_5 = QLabel("Jugadores en Sala:", parent=self)
        self.label1_5.setGeometry(QtCore.QRect(40, 370, 271, 61))
        self.label1_5.setFont(font_label)

        self.jugadores_label = QLabel("<Listado_Jugadores>", parent=self)
        self.jugadores_label.setGeometry(QtCore.QRect(300, 370, 400, 61))
        self.jugadores_label.setFont(font_label)
        
        # Label para el dato de "Jugadores Requeridos"
        
        self.label1_4 = QLabel("Jugadores Requeridos:", parent=self)
        self.label1_4.setGeometry(QtCore.QRect(30, 470,280, 61))
        self.label1_4.setFont(font_label)
        
        self.jugadores_requeridos_label = QLabel("<5>", parent=self)
        self.jugadores_requeridos_label.setGeometry(QtCore.QRect(380, 470, 200, 61))
        self.jugadores_requeridos_label.setFont(font_label)


        self.estado_sala_label = QLabel("<Msg_Estado_Sala>", parent=self)
        self.estado_sala_label.setGeometry(QtCore.QRect(720, 510, 271, 100))
        estado_font = QtGui.QFont("Verdana", 15, QtGui.QFont.Weight.Bold)
        estado_font.setItalic(True)
        self.estado_sala_label.setFont(estado_font)

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
