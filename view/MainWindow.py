from PyQt6.QtWidgets import QPushButton, QMainWindow, QVBoxLayout, QSpinBox, QProgressBar, QComboBox, QLineEdit, QLabel, \
    QGroupBox, QHBoxLayout
from PyQt6.uic import loadUi
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.main_controller import MainController


class MainWindow(QMainWindow):
    grapheLayout: QVBoxLayout

    createButton: QPushButton
    deleteButton: QPushButton
    nbrNodes: QSpinBox

    edgeGroupBox: QGroupBox
    edgeLabel: QLabel
    weightLabel: QLabel
    weightSpinBox: QSpinBox

    def __init__(self):
        super().__init__()
        loadUi("view/ui/main_window.ui", self)
        self.resize(1000, 800)

        # Créer le GroupBox pour l'arête
        self.edgeGroupBox = QGroupBox("Gestion de l'arête")
        edge_layout = QHBoxLayout()

        self.edgeLabel = QLabel("Arête sélectionnée : Aucune")
        self.weightLabel = QLabel("Poids :")
        self.weightSpinBox = QSpinBox()
        self.weightSpinBox.setMinimum(1)
        self.weightSpinBox.setMaximum(100)

        edge_layout.addWidget(self.edgeLabel)
        edge_layout.addStretch()
        edge_layout.addWidget(self.weightLabel)
        edge_layout.addWidget(self.weightSpinBox)

        self.edgeGroupBox.setLayout(edge_layout)
        self.edgeGroupBox.setVisible(False)

        # Ajouter le GroupBox au layout principal
        self.centralwidget.layout().addWidget(self.edgeGroupBox)

        # self.draw_graphe()
        if TYPE_CHECKING:
            self.__controller: MainController | None = None

    def add_canvas(self, canvas):
        #  insérer le canvas dans le layout
        self.grapheLayout.addWidget(canvas)

    def set_controller(self, controller):
        self.__controller = controller