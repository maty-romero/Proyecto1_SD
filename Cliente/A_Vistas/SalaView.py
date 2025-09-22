# sala_view.py
from PyQt6.QtWidgets import QWidget
#from sala_view_ui import Ui_MainWindow
from PyQt6 import QtCore, QtGui, QtWidgets

# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)

class Ui_SalaView(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1080, 720)
        MainWindow.setMinimumSize(QtCore.QSize(1080, 720))
        MainWindow.setMaximumSize(QtCore.QSize(1080, 720))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setBold(True)
        MainWindow.setFont(font)
        self.label = QtWidgets.QLabel(parent=MainWindow)
        self.label.setGeometry(QtCore.QRect(320, 20, 521, 121))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(50)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.confirmar_jugador_btn = QtWidgets.QPushButton(parent=MainWindow)
        self.confirmar_jugador_btn.setGeometry(QtCore.QRect(430, 620, 261, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        self.confirmar_jugador_btn.setFont(font)
        self.confirmar_jugador_btn.setObjectName("confirmar_jugador_btn")
        self.label1 = QtWidgets.QLabel(parent=MainWindow)
        self.label1.setGeometry(QtCore.QRect(60, 160, 241, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(15)
        font.setBold(True)
        self.label1.setFont(font)
        self.label1.setObjectName("label1")
        self.nickname_label = QtWidgets.QLabel(parent=MainWindow)
        self.nickname_label.setGeometry(QtCore.QRect(190, 160, 300, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(15)
        font.setBold(True)
        self.nickname_label.setFont(font)
        self.nickname_label.setObjectName("nickname_label")
        self.label1_2 = QtWidgets.QLabel(parent=MainWindow)
        self.label1_2.setGeometry(QtCore.QRect(700, 170, 241, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(15)
        font.setBold(True)
        self.label1_2.setFont(font)
        self.label1_2.setObjectName("label1_2")
        self.nrorondas_label = QtWidgets.QLabel(parent=MainWindow)
        self.nrorondas_label.setGeometry(QtCore.QRect(920, 170, 101, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(15)
        font.setBold(True)
        self.nrorondas_label.setFont(font)
        self.nrorondas_label.setObjectName("nrorondas_label")
        self.label1_3 = QtWidgets.QLabel(parent=MainWindow)
        self.label1_3.setGeometry(QtCore.QRect(50, 270, 241, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(15)
        font.setBold(True)
        self.label1_3.setFont(font)
        self.label1_3.setObjectName("label1_3")
        self.categorias_label = QtWidgets.QLabel(parent=MainWindow)
        self.categorias_label.setGeometry(QtCore.QRect(220, 270, 600, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(12)
        font.setBold(True)
        self.categorias_label.setFont(font)
        self.categorias_label.setObjectName("categorias_label")
        self.label1_5 = QtWidgets.QLabel(parent=MainWindow)
        self.label1_5.setGeometry(QtCore.QRect(40, 370, 271, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(15)
        font.setBold(True)
        self.label1_5.setFont(font)
        self.label1_5.setObjectName("label1_5")
        self.jugadores_label = QtWidgets.QLabel(parent=MainWindow)
        self.jugadores_label.setGeometry(QtCore.QRect(300, 370, 400, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(15)
        font.setBold(True)
        self.jugadores_label.setFont(font)
        self.jugadores_label.setObjectName("jugadores_label")
        self.estado_sala_label = QtWidgets.QLabel(parent=MainWindow)
        self.estado_sala_label.setGeometry(QtCore.QRect(340, 540, 400, 100))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        self.estado_sala_label.setFont(font)
        self.estado_sala_label.setObjectName("estado_sala_label")

        # Label estático para "Jugadores Requeridos"
        self.label1_6 = QtWidgets.QLabel(parent=MainWindow)
        self.label1_6.setGeometry(QtCore.QRect(50, 440, 241, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(15)
        font.setBold(True)
        self.label1_6.setFont(font)
        self.label1_6.setObjectName("label1_6")

        # Label para el dato de "Jugadores Requeridos"
        self.jugadores_requeridos_label = QtWidgets.QLabel(parent=MainWindow)
        self.jugadores_requeridos_label.setGeometry(QtCore.QRect(320, 440, 100, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(15)
        font.setBold(True)
        self.jugadores_requeridos_label.setFont(font)
        self.jugadores_requeridos_label.setObjectName("jugadores_requeridos_label")

        # # Label estático para "Jugadores Restantes"
        # self.label1_7 = QtWidgets.QLabel(parent=MainWindow)
        # self.label1_7.setGeometry(QtCore.QRect(50, 500, 241, 61))
        # font = QtGui.QFont()
        # font.setFamily("Verdana")
        # font.setPointSize(15)
        # font.setBold(True)
        # self.label1_7.setFont(font)
        # self.label1_7.setObjectName("label1_7")

        # # Label para el dato de "Jugadores Restantes"
        # self.jugadores_restantes_label = QtWidgets.QLabel(parent=MainWindow)
        # self.jugadores_restantes_label.setGeometry(QtCore.QRect(250, 500, 100, 61))
        # font = QtGui.QFont()
        # font.setFamily("Verdana")
        # font.setPointSize(15)
        # font.setBold(True)
        # self.jugadores_restantes_label.setFont(font)
        # self.jugadores_restantes_label.setObjectName("jugadores_restantes_label")



        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Sala"))
        self.label.setText(_translate("MainWindow", "TUTIFRUTTI"))
        self.confirmar_jugador_btn.setText(_translate("MainWindow", "Estoy Listo!"))
        self.label1.setText(_translate("MainWindow", "Jugador:"))
        self.nickname_label.setText(_translate("MainWindow", "<Pepe>"))
        self.label1_2.setText(_translate("MainWindow", "Rondas a Jugar:"))
        self.nrorondas_label.setText(_translate("MainWindow", "<3>"))
        self.label1_3.setText(_translate("MainWindow", "Categorias: "))
        self.categorias_label.setText(_translate("MainWindow", "<Listado_Categorias>"))
        self.label1_5.setText(_translate("MainWindow", "Jugadores en Sala: "))
        self.jugadores_label.setText(_translate("MainWindow", "<Listado_Jugadores>"))
        self.estado_sala_label.setText(_translate("MainWindow", "'Presiona 'Estoy listo!' para unirte al juego'"))

        self.label1_6.setText(_translate("MainWindow", "Jugadores requeridos: "))
        self.jugadores_requeridos_label.setText(_translate("MainWindow", "<Min>"))
        # self.label1_7.setText(_translate("MainWindow", "Jugadores restantes:"))
        # self.jugadores_restantes_label.setText(_translate("MainWindow", "<X>"))


    def setJugadoresRestantes(self,jug_rest):
        self.jugadores_restantes_label.setText(jug_rest)

    def setJugadoresRequeridos(self,jug_req):
        self.jugadores_requeridos_label.setText(jug_req)

    def setNombreJugador(self, nombre):
        self.nickname_label.setText(nombre)

    def getNombreJugador(self):
        return self.nickname_label.text()

    def setRonda(self,cantRondas):
        self.nrorondas_label.setText(cantRondas)


    def setListaCategoria(self,categorias):
        self.categorias_label.setText(categorias)

    def setEstadoSala(self,estadoSala):
        self.estado_sala_label.setText(estadoSala)
        
    def setListaJugadores(self,jugadores):
        self.jugadores_label.setText(jugadores)

    def getUnirSala(self):
        return self.confirmar_jugador_btn
    
    def setJugadoresRequeridos(self,jugadores):
        self.jugadores_requeridos_label.setText(jugadores)

    # def setJugadoresRestantes(self,jugadores):
    #     self.jugadores_restantes_label.setText(jugadores)