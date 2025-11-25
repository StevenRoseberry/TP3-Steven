from PyQt6.QtWidgets import QPushButton, QMainWindow, QVBoxLayout, QSpinBox, QProgressBar, QLabel, QGroupBox
from PyQt6.uic import loadUi
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.main_controller import MainController


class MainWindow(QMainWindow):
    # Layout principal
    grapheLayout: QVBoxLayout

    # Contrôles de base
    createButton: QPushButton
    deleteButton: QPushButton
    nbrNodes: QSpinBox

    # Gestion des arêtes
    edgeGroupBox: QGroupBox
    edgeLabel: QLabel
    weightLabel: QLabel
    weightSpinBox: QSpinBox

    # Plus court chemin
    pathGroupBox: QGroupBox
    findPathButton: QPushButton
    resetPathButton: QPushButton
    pathStatusLabel: QLabel
    pathProgressBar: QProgressBar

    # Parcours
    traversalGroupBox: QGroupBox
    traversalInfoLabel: QLabel
    traversalStatusLabel: QLabel
    traversalProgressBar: QProgressBar

    # Légende
    legendGroupBox: QGroupBox

    def __init__(self):
        super().__init__()
        loadUi("view/ui/main_window.ui", self)
        self.resize(1200, 900)

        if TYPE_CHECKING:
            self.__controller: MainController | None = None

    def add_canvas(self, canvas):
        """Insère le canvas dans le layout"""
        self.grapheLayout.addWidget(canvas)

    def set_controller(self, controller):
        self.__controller = controller