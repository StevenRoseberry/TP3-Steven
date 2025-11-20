from model.graphe_model import GrapheModel
from view.GrapheCanvas import GraphCanvas
from view.MainWindow import MainWindow


class MainController:
    __view: MainWindow
    __model: GrapheModel
    __canvas: GraphCanvas

    def __init__(self, view, model, canvas):
        self.__view = view
        self.__model = model
        self.__canvas = canvas
        self.__view.createButton.clicked.connect(self.generate_graph)
        self.__view.deleteButton.clicked.connect(self.delete_graph)

    def post_init(self):
        self.__model.grapheChanged.connect(self.__canvas.on_graph_changed)
        self.__model.grapheChanged.emit(self.__model.pos)

    def graphe(self):
        return self.__model.graphe

    @property
    def _model(self):
        return self.__model

    def generate_graph(self):
        self.__model.generate_graph()

    def delete_graph(self):
        self.__model.delete_graph()