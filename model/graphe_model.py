import random
import networkx as nx
from PyQt6.QtCore import pyqtSignal, QObject
from networkx import Graph


class GrapheModel(QObject):
    _graphe: Graph = nx.Graph()
    _pos = None
    _selected_node = None
    _dragging_node = None
    _selected_edge = None
    _start_node = None  # Sommet de départ pour plus court chemin
    _end_node = None  # Sommet d'arrivée pour plus court chemin
    _shortest_path = []  # Stocker le plus court chemin
    _visited_nodes = []  # Stocker les nœuds visités pendant le parcours

    __proba = 0.5
    __default_graphe_order = 10
    __poids_min = 1
    __poids_max = 10

    grapheChanged = pyqtSignal(dict)
    pathFound = pyqtSignal(list)  # Signal quand le chemin est trouvé
    nodeVisited = pyqtSignal(int)  # Signal quand un nœud est visité
    traversalComplete = pyqtSignal()  # Signal quand le parcours est terminé

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

    @property
    def selected_edge(self):
        return self._selected_edge

    @selected_edge.setter
    def selected_edge(self, edge):
        self._selected_edge = edge

    @property
    def start_node(self):
        return self._start_node

    @start_node.setter
    def start_node(self, node):
        self._start_node = node
        self.grapheChanged.emit(self._pos)

    @property
    def end_node(self):
        return self._end_node

    @end_node.setter
    def end_node(self, node):
        self._end_node = node
        self.grapheChanged.emit(self._pos)

    @property
    def shortest_path(self):
        return self._shortest_path

    @shortest_path.setter
    def shortest_path(self, path):
        self._shortest_path = path
        self.grapheChanged.emit(self._pos)

    @property
    def visited_nodes(self):
        return self._visited_nodes

    @visited_nodes.setter
    def visited_nodes(self, nodes):
        self._visited_nodes = nodes
        self.grapheChanged.emit(self._pos)

    def edge_weight(self, edge):
        return self._graphe[edge[0]][edge[1]]['weight']

    def generate_graph(self):
        self._graphe = nx.gnp_random_graph(self.default_graphe_order, self.__proba, directed=False)
        for u, v in self._graphe.edges():
            self._graphe[u][v]['weight'] = random.randint(self.__poids_min, self.__poids_max)
        self._pos = nx.spring_layout(self._graphe, seed=42)
        self._selected_node = None
        self._selected_edge = None
        self._start_node = None
        self._end_node = None
        self._shortest_path = []
        self._visited_nodes = []
        self.grapheChanged.emit(self._pos)

    def delete_graph(self):
        self._graphe = nx.empty_graph()
        self._pos = nx.spring_layout(self._graphe, seed=42)
        self._selected_node = None
        self._selected_edge = None
        self._start_node = None
        self._end_node = None
        self._shortest_path = []
        self._visited_nodes = []
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
            if self._start_node == node:
                self._start_node = None
            if self._end_node == node:
                self._end_node = None
            self.grapheChanged.emit(self._pos)

    def delete_edge(self, edge):
        node1, node2 = edge
        if self._graphe.has_edge(node1, node2):
            self._graphe.remove_edge(node1, node2)
            if self._selected_edge == edge or self._selected_edge == (node2, node1):
                self._selected_edge = None
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

    def set_edge_weight(self, edge, weight):
        node1, node2 = edge
        if self._graphe.has_edge(node1, node2):
            self._graphe[node1][node2]['weight'] = weight
            self.grapheChanged.emit(self._pos)
            return True
        elif self._graphe.has_edge(node2, node1):
            self._graphe[node2][node1]['weight'] = weight
            self.grapheChanged.emit(self._pos)
            return True
        return False

    def get_edge_weight(self, edge):
        node1, node2 = edge
        if self._graphe.has_edge(node1, node2):
            return self._graphe[node1][node2]['weight']
        elif self._graphe.has_edge(node2, node1):
            return self._graphe[node2][node1]['weight']
        return None

    def find_shortest_path(self):
        if self._start_node is None or self._end_node is None:
            return []

        if self._start_node not in self._graphe.nodes() or self._end_node not in self._graphe.nodes():
            return []

        try:
            # Utiliser dijkstra pour tenir compte des poids
            path = nx.shortest_path(self._graphe, source=self._start_node,
                                    target=self._end_node, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return []

    def reset_path(self):
        self._start_node = None
        self._end_node = None
        self._shortest_path = []
        self.grapheChanged.emit(self._pos)

    def reset_traversal(self):
        self._visited_nodes = []
        self.grapheChanged.emit(self._pos)