from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1366, 768)
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        MainWindow.setStyleSheet("background-color: rgb(255, 192, 252);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Crear un layout vertical para la ventana central
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # Etiquetas para la ronda y la letra, centradas en la parte superior
        header_layout = QtWidgets.QHBoxLayout()  # Layout horizontal para la parte superior
        self.labelRondaConNumero = QtWidgets.QLabel(self.centralwidget)
        self.labelRondaConNumero.setText("Ronda: 1/2")
        self.labelRondaConNumero.setStyleSheet("font: 22pt 'Segoe UI'; font: 700 22pt 'Segoe UI';")
        self.labelLetraRandom = QtWidgets.QLabel(self.centralwidget)
        self.labelLetraRandom.setText("Letra: T")
        self.labelLetraRandom.setStyleSheet("font: 700 14pt 'Segoe UI';")
        header_layout.addWidget(self.labelRondaConNumero)
        header_layout.addWidget(self.labelLetraRandom)
        main_layout.addLayout(header_layout)

        # Información adicional, centrada debajo de la ronda y letra
        self.LabelDeInformacion = QtWidgets.QLabel(self.centralwidget)
        self.LabelDeInformacion.setText("Indicar si la respuesta de tus rivales son válidas o no en los checkboxes")
        self.LabelDeInformacion.setStyleSheet("color: rgb(0, 0, 0); font: 700 12pt 'Segoe UI'; background-color: rgb(216, 253, 255);")
        self.LabelDeInformacion.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.LabelDeInformacion)

        # Crear un área de desplazamiento para las categorías
        self.scroll_area = QtWidgets.QScrollArea(self.centralwidget)
        self.scroll_area.setWidgetResizable(True)  # Para que el contenido se ajuste al área de desplazamiento
        self.scroll_area_widget_contents = QtWidgets.QWidget()
        self.scroll_area.setWidget(self.scroll_area_widget_contents)

        # Layout vertical para las categorías dentro del scroll area
        scroll_layout = QtWidgets.QVBoxLayout(self.scroll_area_widget_contents)

        # Definir las categorías
        categorias = ["Animal con T", "Color con T", "Objeto con T", "Pais con T"]

        # Establecer la cantidad de jugadores (ajustable)
        num_jugadores = 3

        # Crear un widget para cada categoría
        for categoria in categorias:
            # Crear un QGroupBox para cada categoría con bordes y fondo
            group_box = QtWidgets.QGroupBox(categoria)
            group_box.setStyleSheet("background-color: rgb(255, 255, 255); border: 2px solid rgb(0, 85, 255); margin: 10px; padding: 10px;")
            
            # Crear un layout dentro del QGroupBox
            group_box_layout = QtWidgets.QVBoxLayout(group_box)

            # Agregar los jugadores a la categoría en filas
            for i in range(num_jugadores):
                # Crear un QHBoxLayout para los elementos en una fila
                row_layout = QtWidgets.QHBoxLayout()
                
                # Crear QLabel para la imagen del jugador
                image_label = QtWidgets.QLabel()
                pixmap = QtGui.QPixmap("img/jugadorconectadocincuenta.png")  # Aquí pon la ruta correcta de la imagen
                #pixmap = pixmap.scaled(50, 50, QtCore.Qt.AspectRatioMode.KeepAspectRatio)  # Ajustar tamaño de la imagen (50x50)
                image_label.setPixmap(pixmap)
                image_label.setFixedSize(50, 50)  # Establecer un tamaño fijo para la imagen
                row_layout.addWidget(image_label)  # Agregar la imagen al lado del texto

        
                player_label = QtWidgets.QLabel(f"Jugador {i+1}")
                response_label = QtWidgets.QLabel(f"Respuesta {i+1}")
                check_box = QtWidgets.QCheckBox("Válido")
                
                # Alinear los elementos en la fila
                row_layout.addWidget(player_label)
                row_layout.addWidget(response_label)
                row_layout.addWidget(check_box)

                # Añadir la fila al QGroupBox
                group_box_layout.addLayout(row_layout)

            # Agregar una línea divisoria para separar las categorías
            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
            group_box_layout.addWidget(line)

            # Agregar el QGroupBox al layout principal
            scroll_layout.addWidget(group_box)

        # Agregar el área de desplazamiento al layout principal
        main_layout.addWidget(self.scroll_area)

        # Mover el botón "ENVIAR VOTO" al final
        self.pushButtonEnviarVoto = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonEnviarVoto.setText("ENVIAR VOTO")
        self.pushButtonEnviarVoto.setStyleSheet("background-color: rgb(0, 85, 255); color: rgb(255, 255, 255); font: 700 14pt 'Segoe UI';")
        self.pushButtonEnviarVoto.setObjectName("pushButtonEnviarVoto")
        self.pushButtonEnviarVoto.setEnabled(True)
        main_layout.addWidget(self.pushButtonEnviarVoto)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1366, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    
    def get_boton_confirmar_voto(self):
        return self.pushButtonEnviarVoto
    
