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
        self.__view.weightSpinBox.valueChanged.connect(self.apply_edge_weight)

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

    def update_edge_ui(self):
        #Met à jour l'affichage de l'arête sélectionnée et son poids
        if self.__canvas._selected_edge is None:
            self.__view.edgeGroupBox.setVisible(False)
        else:
            self.__view.edgeGroupBox.setVisible(True)
            edge = self.__canvas._selected_edge
            weight = self.__model.get_edge_weight(edge)
            self.__view.edgeLabel.setText(f"Arête sélectionnée : {edge[0]} - {edge[1]}")
            self.__view.weightSpinBox.blockSignals(True)
            self.__view.weightSpinBox.setValue(weight if weight else 1)
            self.__view.weightSpinBox.blockSignals(False)

    def apply_edge_weight(self):
        if self.__canvas._selected_edge is None:
            return

        new_weight = self.__view.weightSpinBox.value()
        self.__model.set_edge_weight(self.__canvas._selected_edge, new_weight)
        self.__canvas.draw_graphe()