# main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
#from WorkingMainWindow import Ui_MainWindow  # generado por pyuic6
from PyQt6 import QtCore, QtGui, QtWidgets

"""
    Vista Principal que puede inyectar otras vistas. Respetar en todas las vistas y 
    MainWindow un tamaño fijo. 
"""
#  
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1080, 720) 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Asegurar layout en centralContainer
        if self.ui.centralContainer.layout() is None:
            layout = QVBoxLayout()
            self.ui.centralContainer.setLayout(layout)

    def inject_view(self, view_class):
        layout = self.ui.centralContainer.layout()

        # Limpiar vista anterior
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

        # Inyectar nueva vista
        widget = QWidget()
        view = view_class()
        view.ui.setupUi(widget)
        layout.addWidget(widget)

# Clase Ui Usada como Layout 
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
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))