# sala_view.py
from PyQt6.QtWidgets import QWidget
#from sala_view_ui import Ui_SalaView
#from ronda_view_ui import Ui_MainWindow
from PyQt6 import QtCore, QtGui, QtWidgets

# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)

class Ui_RondaView(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1080, 720)
        MainWindow.setMinimumSize(QtCore.QSize(1080, 720))
        MainWindow.setMaximumSize(QtCore.QSize(1080, 720))
        #ETIQUETA RONDA
        self.label = QtWidgets.QLabel(parent=MainWindow)
        self.label.setGeometry(QtCore.QRect(40, 0, 200, 121))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(40)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        
        self.nroronda_label = QtWidgets.QLabel(parent=MainWindow)
        self.nroronda_label.setGeometry(QtCore.QRect(250, 0, 150, 121))  # Ajusté la posición
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(30)  # Reducido el tamaño de la fuente a 35
        font.setBold(True)
        self.nroronda_label.setFont(font)
        self.nroronda_label.setObjectName("nroronda_label")
        
        
        # Etiqueta "Letra:"
        self.lettra_texto_label = QtWidgets.QLabel(parent=MainWindow)
        self.lettra_texto_label.setGeometry(QtCore.QRect(750, 0, 190, 121))  # Posicionada junto a la ronda
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(40)
        font.setBold(True)
        self.lettra_texto_label.setFont(font)
        self.lettra_texto_label.setObjectName("lettra_texto_label")

        # Etiqueta para mostrar la letra aleatoria
        self.letra_label = QtWidgets.QLabel(parent=MainWindow)
        self.letra_label.setGeometry(QtCore.QRect(940, 0, 80, 121))  # Posicionada junto a "Letra:"
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(40)
        font.setBold(True)
        self.letra_label.setFont(font)
        self.letra_label.setObjectName("letra_label")
        
        
        
        self.enviar_respuestas_btn = QtWidgets.QPushButton(parent=MainWindow)
        self.enviar_respuestas_btn.setGeometry(QtCore.QRect(420, 610, 261, 61))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        font.setBold(True)
        

        
        # Botón "STOP!"
        self.enviar_respuestas_btn.setFont(font)
        self.enviar_respuestas_btn.setObjectName("enviar_respuestas_btn")
        self.input_categoria1 = QtWidgets.QLineEdit(parent=MainWindow)
        self.input_categoria1.setGeometry(QtCore.QRect(400, 140, 481, 41))
        self.input_categoria1.setObjectName("input_categoria1")
        self.categoria1_label = QtWidgets.QLabel(parent=MainWindow)
        self.categoria1_label.setGeometry(QtCore.QRect(80, 140, 301, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.categoria1_label.setFont(font)
        self.categoria1_label.setObjectName("categoria1_label")
        self.categoria2_label = QtWidgets.QLabel(parent=MainWindow)
        self.categoria2_label.setGeometry(QtCore.QRect(80, 230, 301, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.categoria2_label.setFont(font)
        self.categoria2_label.setObjectName("categoria2_label")
        self.input_categoria2 = QtWidgets.QLineEdit(parent=MainWindow)
        self.input_categoria2.setGeometry(QtCore.QRect(400, 230, 481, 41))
        self.input_categoria2.setObjectName("input_categoria2")
        self.categoria3_label = QtWidgets.QLabel(parent=MainWindow)
        self.categoria3_label.setGeometry(QtCore.QRect(80, 320, 301, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.categoria3_label.setFont(font)
        self.categoria3_label.setObjectName("categoria3_label")
        self.input_categoria3 = QtWidgets.QLineEdit(parent=MainWindow)
        self.input_categoria3.setGeometry(QtCore.QRect(400, 320, 481, 41))
        self.input_categoria3.setObjectName("input_categoria3")
        self.categoria4_label = QtWidgets.QLabel(parent=MainWindow)
        self.categoria4_label.setGeometry(QtCore.QRect(80, 410, 301, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.categoria4_label.setFont(font)
        self.categoria4_label.setObjectName("categoria4_label")
        self.input_categoria4 = QtWidgets.QLineEdit(parent=MainWindow)
        self.input_categoria4.setGeometry(QtCore.QRect(400, 410, 481, 41))
        self.input_categoria4.setObjectName("input_categoria4")
        self.input_categoria5 = QtWidgets.QLineEdit(parent=MainWindow)
        self.input_categoria5.setGeometry(QtCore.QRect(400, 500, 481, 41))
        self.input_categoria5.setObjectName("input_categoria5")
        self.categoria5_label = QtWidgets.QLabel(parent=MainWindow)
        self.categoria5_label.setGeometry(QtCore.QRect(80, 500, 301, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.categoria5_label.setFont(font)
        self.categoria5_label.setObjectName("categoria5_label")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Ronda"))
        self.label.setText(_translate("MainWindow", "Ronda"))
        self.nroronda_label.setText(_translate("MainWindow", "<1/3>"))
        self.enviar_respuestas_btn.setText(_translate("MainWindow", "STOP!"))
        self.categoria1_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">&lt;Categoria1&gt;</p></body></html>"))
        self.categoria2_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">&lt;Categoria2&gt;</p></body></html>"))
        self.categoria3_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">&lt;Categoria3&gt;</p></body></html>"))
        self.categoria4_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">&lt;Categoria4&gt;</p></body></html>"))
        self.categoria5_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">&lt;Categoria5&gt;</p></body></html>"))
        self.lettra_texto_label.setText(_translate("MainWindow", "Letra:"))
        self.letra_label.setText(_translate("MainWindow", "R"))  
        

    def obtener_categorias(self):
        return [self.categoria1_label,
                self.categoria2_label,
                self.categoria3_label,
                self.categoria4_label,
                self.categoria5_label]
        
        
    def set_numero_ronda(self,ronda, totalRondas):
        self.nroronda_label.setText(f"{ronda}/{totalRondas}")
        
    
    def setLetraAleatoria(self, letra):
        self.letra_label.setText(letra)