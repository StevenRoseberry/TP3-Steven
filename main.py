import sys
from controller.main_controller import MainController
from model.graphe_model import GrapheModel
from view.GrapheCanvas import GraphCanvas
from view.MainWindow import MainWindow
from PyQt6.QtWidgets import QApplication
import traceback
import matplotlib


#LE CHANGEMENT DE THÈME EST COPIÉ DU TP2, j'ai adapté les thèmes avec ClaudeAI et pour l'implémentation aussi !!
#Le UI a aussi été "modernisé" avec ClaudeAI, gros remerciment à mon beau gosse Claude pour vrai
if __name__ == "__main__":
    def qt_exception_hook(exctype, value, tb):
        traceback.print_exception(exctype, value, tb)

    sys.excepthook = qt_exception_hook

    app = QApplication(sys.argv)

    # Configurer matplotlib pour le thème dark par défaut
    matplotlib.rcParams['figure.facecolor'] = '#2b2b2b'
    matplotlib.rcParams['axes.facecolor'] = '#2b2b2b'
    matplotlib.rcParams['axes.edgecolor'] = '#e0e0e0'
    matplotlib.rcParams['axes.labelcolor'] = '#e0e0e0'
    matplotlib.rcParams['text.color'] = '#e0e0e0'
    matplotlib.rcParams['xtick.color'] = '#e0e0e0'
    matplotlib.rcParams['ytick.color'] = '#e0e0e0'
    matplotlib.rcParams['grid.color'] = '#555555'
    matplotlib.rcParams['legend.facecolor'] = '#2b2b2b'
    matplotlib.rcParams['legend.edgecolor'] = '#e0e0e0'
    matplotlib.rcParams['savefig.facecolor'] = '#2b2b2b'

    # Créer les composants
    canvas = GraphCanvas()
    fenetre = MainWindow(app)  # Passer l'app pour le toggle theme
    fenetre.add_canvas(canvas)
    model = GrapheModel()
    controller = MainController(fenetre, model, canvas)
    fenetre.set_controller(controller)
    canvas.set_controller(controller)
    controller.post_init()
    fenetre.show()

    sys.exit(app.exec())