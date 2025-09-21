from Controladores.ControladorSalaView import ControladorSalaView
from Vistas.testVistas.SalaView import Ui_SalaView
from PyQt6 import QtWidgets

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    controlador = ControladorSalaView()
    sys.exit(app.exec())