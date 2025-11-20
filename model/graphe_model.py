import random
import networkx as nx
from PyQt6.QtCore import pyqtSignal, QObject
from networkx import Graph


class GrapheModel(QObject):
    _graphe: Graph = nx.Graph()
    _pos = None
    _selected_node = None
    _dragging_node = None

    __proba = 0.5
    __default_graphe_order = 10
    __poids_min = 1
    __poids_max = 10

    grapheChanged = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._pos = nx.spring_layout(self._graphe, seed=42)

    def graphe_order(self):
        return self._graphe.number_of_nodes()

    @property
    def default_graphe_order(self):
        return self.__default_graphe_order

    @default_graphe_order.setter
    def default_graphe_order(self, value):
        self.__default_graphe_order = value

    @property
    def graphe(self):
        return self._graphe

    @property
    def pos(self):
        return self._pos

    @property
    def selected_node(self):
        return self._selected_node

    @selected_node.setter
    def selected_node(self, node):
        self._selected_node = node

    def edge_weight(self, edge):
        return self._graphe[edge[0]][edge[1]]['weight']

    def generate_graph(self):
        self._graphe = nx.gnp_random_graph(self.default_graphe_order, self.__proba, directed=False)
        for u, v in self._graphe.edges():
            self._graphe[u][v]['weight'] = random.randint(self.__poids_min, self.__poids_max)
        self._pos = nx.spring_layout(self._graphe, seed=42)
        self._selected_node = None
        self.grapheChanged.emit(self._pos)

    def delete_graph(self):
        self._graphe = nx.empty_graph()
        self._pos = nx.spring_layout(self._graphe, seed=42)
        self._selected_node = None
        self.grapheChanged.emit(self._pos)

    def add_node(self, position):
        new_node_id = 0
        while new_node_id in self._graphe.nodes():
            new_node_id += 1
        self._graphe.add_node(new_node_id)
        self._pos[new_node_id] = position
        self.grapheChanged.emit(self._pos)

    def delete_node(self, node):
        if node in self._graphe.nodes():
            self._graphe.remove_node(node)
            if node in self._pos:
                del self._pos[node]
            if self._selected_node == node:
                self._selected_node = None
            self.grapheChanged.emit(self._pos)

    def move_node(self, node, position):
        if node in self._graphe.nodes():
            self._pos[node] = position
            self.grapheChanged.emit(self._pos)

    def add_edge(self, node1, node2, weight=1):
        if node1 in self._graphe.nodes() and node2 in self._graphe.nodes():
            if not self._graphe.has_edge(node1, node2):
                self._graphe.add_edge(node1, node2, weight=weight)
                self.grapheChanged.emit(self._pos)
                return True
        return False