import networkx as nx
from PyQt6.QtCore import Qt

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from networkx import NetworkXError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.main_controller import MainController  # uniquement pour

class GraphCanvas(FigureCanvasQTAgg):
    _pos=None

    def __init__(self):
        # Crée une figure matplotlib
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        super().__init__(self.fig)
        #self.draw_graphe()
        if TYPE_CHECKING:
            self.__controller: MainController | None = None
        #Permet de faire fonctionner l'ecoute des touches dans un canvas
        self.setFocus()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_controller(self,controller):
        self.__controller=controller

    def __convert_pos(self, event):
        """ Cette methode permet de transformer les coordonnées d'un mouseEvent
         (coordonnées QT) en coordonnées figures matplotlib """
        # coordonnées de l’événement en pixels figure
        x_fig, y_fig = self.mouseEventCoords(event)

        # transformation : des pixels figure → data coords
        return self.ax.transData.inverted().transform((x_fig, y_fig))

    def draw_graphe(self):
        # Effacer le contenu précédent
        self.ax.clear()
        self.__draw_graphe()
        self.draw()

    def __draw_graphe(self):
        if self.__controller.graphe() is None:
            return
        try :
            # Dessiner le graphe dans l'axe du canvas
            nx.draw(self.__controller.graphe(), self._pos , with_labels=True, node_color='skyblue', node_size=800)
            labels = nx.get_edge_attributes(self.__controller.graphe(), "weight")
            nx.draw_networkx_edge_labels(self.__controller.graphe(), self._pos , edge_labels=labels)
        except NetworkXError as nxe :
            print("__draw_graphe, Erreur inatendue:",nxe)
        except Exception as e :
            print("__draw_graphe, Erreur inatendue:",e)


    def on_graph_changed(self,position):
        self._pos = position
        self.draw_graphe()

    def mousePressEvent(self, event):
        print("clic clic")
        print(self.__convert_pos(event))
        self._pos = self.__convert_pos(event)

