import sys

from controller.main_controller import MainController
from model.graphe_model import GrapheModel
from view.GrapheCanvas import GraphCanvas
from view.MainWindow import MainWindow
from PyQt6.QtWidgets import QApplication
import sys
import traceback

if __name__ == "__main__":
    def qt_exception_hook(exctype, value, tb):
        traceback.print_exception(exctype, value, tb)


    sys.excepthook = qt_exception_hook

    app = QApplication(sys.argv)
    canvas = GraphCanvas()
    fenetre = MainWindow()
    fenetre.add_canvas(canvas)
    model = GrapheModel()
    controller = MainController(fenetre,model,canvas)
    fenetre.set_controller(controller)
    canvas.set_controller(controller)
    controller.post_init()
    fenetre.show()


    sys.exit(app.exec())
