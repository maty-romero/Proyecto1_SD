from controlador.ControladorPuntajes import ControladorPuntajes
from controlador.ControladorVotaciones import ControladorVotaciones

from PyQt6 import QtWidgets

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    controlador = ControladorVotaciones()
    sys.exit(app.exec())