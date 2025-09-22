from PyQt6.QtWidgets import QMainWindow, QStackedWidget
#from ui_mainwindow import Ui_MainWindow  # generado por pyuic6
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QVBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1080, 720)
        self.setObjectName("Ventana Principal")

        # Carga diseño desde Qt Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Crea stack para las vistas
        self.stack = QStackedWidget()

        # Asegurarse que centralContainer tenga un layout
        if self.ui.centralContainer.layout() is None:
            layout = QVBoxLayout()
            self.ui.centralContainer.setLayout(layout)

        # Agregar el stack al layout del centralContainer
        self.ui.centralContainer.layout().addWidget(self.stack)

        # Opcional: mostrar ventana
        self.show()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        #self.setFixedSize(1280, 720)
        MainWindow.setFixedSize(1280, 720) # IMPORTANTE
        
        self.centralWidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        MainWindow.setCentralWidget(self.centralWidget)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.centralContainer = QtWidgets.QWidget(parent=self.centralWidget)
        self.centralContainer.setObjectName("centralContainer")
        self.verticalLayout.addWidget(self.centralContainer)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))