# main.py
from PyQt6.QtWidgets import QApplication
from MainWindow import MainWindow
from SalaView import SalaView
from RondaView import RondaView

"""
    Comando: pyuic6 <dssa>.ui -o <saas>.py
    ** Proceso que se siguio para inyectar vistas en MainWindow (vista o ventana principal)

    1. Crear vistas con QTDesigner (Setear Tamaño minimo y maximo a 1080x720)
        - nombrar <nombre_vista>_view.ui  
    2. Cambiar en fichero .ui: 
        <class>RondaView</class>
        <widget class="QWidget" name="RondaView"> -- segun corresponda
    3. Una vez hecha la vista --> Compilar fichero .ui a .py con sig comando en terminal:
        $ pyuic6 <nombre_vista>_view.ui -o <vista>View.py
        Ej: pyuic6 ronda_view.ui -o RondaView.py
    4. Crear una clase como las otras: RondaView, Sala View e insertar codigo generado en 3.
    5. Ajustar imports y demas 
    6. Ya se puede llamar desde la clase que manipula MainWindow e inyectar la vista.
    7. Acceder a atributos o componentes
        SalaView.ui.<componente/widget>.<metodo> 
    8. Cada vista maneja o inyecta los datos necesarios 
"""

app = QApplication([])
window = MainWindow()
window.inject_view(SalaView) # RondaView, SalaView, etc...
window.show()
app.exec()
