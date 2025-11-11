from PyQt6.QtWidgets import QPushButton, QMainWindow, QVBoxLayout, QSpinBox, QProgressBar, QComboBox, QLineEdit
from PyQt6.uic import loadUi
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.main_controller import MainController  # uniquement pour

class MainWindow(QMainWindow):
    grapheLayout:QVBoxLayout

    createButton: QPushButton
    deleteButton: QPushButton
    nbrNodes:QSpinBox

    edgesComboBox:QComboBox
    weightSpinBox:QSpinBox
    deleteEdgeButton:QPushButton



    def __init__(self):
        super().__init__()
        loadUi("view/ui/main_window.ui", self)
        self.resize(1000,800)
        #self.draw_graphe()
        if TYPE_CHECKING:
            self.__controller: MainController | None = None


    def add_canvas(self, canvas):
        #  insérer le canvas dans le layout
        self.grapheLayout.addWidget(canvas)

    def set_controller(self,controller):
        self.__controller = controller