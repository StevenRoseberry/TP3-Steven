from PyQt6.QtWidgets import QPushButton, QMainWindow, QVBoxLayout, QSpinBox, QProgressBar, QLabel, QGroupBox, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi
from typing import TYPE_CHECKING
import matplotlib

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

    def __init__(self, app):
        super().__init__()
        loadUi("view/ui/main_window.ui", self)
        self.resize(1400, 900)
        self.setMinimumSize(1200, 800)

        self.__app = app
        self.__is_dark_mode = True

        if TYPE_CHECKING:
            self.__controller: MainController | None = None

        # Configurer le bouton de toggle theme
        self.__setup_theme_toggle()

        # Charger le thème dark par défaut
        self.__apply_theme()

    def __setup_theme_toggle(self):
        #Configure le bouton de changement de thème dans la menubar
        self.__theme_toggle_button = QPushButton("🌙")
        self.__theme_toggle_button.setObjectName("themeToggleButton")
        self.__theme_toggle_button.setToolTip("Basculer entre mode clair et sombre")
        self.__theme_toggle_button.clicked.connect(self.__toggle_theme)

        # Créer un conteneur pour le bouton
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(self.__theme_toggle_button)
        layout.setContentsMargins(0, 0, 10, 0)

        # Ajouter le bouton dans le coin droit de la menubar
        self.menubar.setCornerWidget(container, Qt.Corner.TopRightCorner)

    def __toggle_theme(self):
        #Bascule entre le thème dark et light
        self.__is_dark_mode = not self.__is_dark_mode
        self.__apply_theme()

    def __apply_theme(self):
        # Applique le thème sélectioné
        if self.__is_dark_mode:
            theme_file = "view/styles/dark_theme.qss"
            self.__theme_toggle_button.setText("🌙")
            bg_color = '#2b2b2b'
            text_color = '#e0e0e0'
        else:
            theme_file = "view/styles/light_theme.qss"
            self.__theme_toggle_button.setText("☀️")
            bg_color = '#f5f5f5'
            text_color = '#333333'

        # Charger le fichier QSS
        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                self.__app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Erreur lors du chargement du thème: {e}")

        # Mettre à jour les couleurs matplotlib
        self.__update_matplotlib_colors(bg_color, text_color)

    def __update_matplotlib_colors(self, bg_color, text_color):
        #Met à jour les couleurs par défaut de matplotlib
        matplotlib.rcParams['figure.facecolor'] = bg_color
        matplotlib.rcParams['axes.facecolor'] = bg_color
        matplotlib.rcParams['axes.edgecolor'] = text_color
        matplotlib.rcParams['axes.labelcolor'] = text_color
        matplotlib.rcParams['text.color'] = text_color
        matplotlib.rcParams['xtick.color'] = text_color
        matplotlib.rcParams['ytick.color'] = text_color
        matplotlib.rcParams['grid.color'] = '#555555' if self.__is_dark_mode else '#cccccc'
        matplotlib.rcParams['legend.facecolor'] = bg_color
        matplotlib.rcParams['legend.edgecolor'] = text_color

        # Redessiner le canvas si le controller est disponible
        if hasattr(self, '_MainWindow__controller') and self.__controller:
            canvas = self.__controller._MainController__canvas
            if canvas and hasattr(canvas, 'draw_graphe'):
                canvas.draw_graphe()

    def add_canvas(self, canvas):
        #Insère le canvas dans le layout
        self.grapheLayout.addWidget(canvas)

    def set_controller(self, controller):
        self.__controller = controller