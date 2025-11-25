import networkx as nx
from PyQt6.QtCore import Qt
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from networkx import NetworkXError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.main_controller import MainController


class GraphCanvas(FigureCanvasQTAgg):
    _pos = None
    _dragging_node = None
    _drag_start_pos = None
    _drag_threshold = 5
    _selected_edge = None

    def __init__(self):
        # Création de la figure matplotlib
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        super().__init__(self.fig)

        if TYPE_CHECKING:
            self.__controller: MainController | None = None

        # Permet de faire fonctionner l'ecoute des touches dans un canvas
        self.setFocus()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_controller(self, controller):
        self.__controller = controller

    # Conversion coordonnées souris en mplotlib
    def _convert_pos(self, event):
        x_fig, y_fig = self.mouseEventCoords(event)
        return self.ax.transData.inverted().transform((x_fig, y_fig))

    # Cherche un noeud proche du clic
    def _find_node_at_position(self, pos, radius=0.05):
        graphe = self.__controller.graphe()
        if graphe is None or len(graphe.nodes()) == 0:
            return None

        min_distance = float('inf')
        closest_node = None

        for node in graphe.nodes():
            if node in self._pos:
                node_pos = np.array(self._pos[node])
                click_pos = np.array(pos)
                distance = np.linalg.norm(node_pos - click_pos)

                # Si clic assez proche d'un noeud, la sélection se fait
                if distance < min_distance and distance < radius:
                    min_distance = distance
                    closest_node = node

        return closest_node

    # Calcul de la distance d'un point à un segment (géométrie vectorielle)
    def _distance_point_to_segment(self, point, seg_start, seg_end):
        # Calcule la distance d'un point à un segment.
        # Utilise la projection orthogonale du point sur la droite du segment.

        point = np.array(point)
        seg_start = np.array(seg_start)
        seg_end = np.array(seg_end)

        # Vecteur du segment
        seg_vec = seg_end - seg_start
        seg_length_sq = np.dot(seg_vec, seg_vec)

        # Si le segment est réduit à un point
        if seg_length_sq == 0:
            return np.linalg.norm(point - seg_start)

        # Paramètre t de la projection du point sur la droite du segment
        # t = 0 correspond à seg_start, t = 1 correspond à seg_end
        t = max(0, min(1, np.dot(point - seg_start, seg_vec) / seg_length_sq))

        # Point projeté sur le segment
        projection = seg_start + t * seg_vec

        # Distance du point à sa projection
        return np.linalg.norm(point - projection)

    # Cherche une arête proche du clic
    def _find_edge_at_position(self, pos, radius=0.05):
        graphe = self.__controller.graphe()
        if graphe is None or len(graphe.edges()) == 0:
            return None

        min_distance = float('inf')
        closest_edge = None

        for edge in graphe.edges():
            node1, node2 = edge
            if node1 in self._pos and node2 in self._pos:
                seg_start = self._pos[node1]
                seg_end = self._pos[node2]

                distance = self._distance_point_to_segment(pos, seg_start, seg_end)

                # Si clic assez proche d'une arête
                if distance < min_distance and distance < radius:
                    min_distance = distance
                    closest_edge = edge

        return closest_edge

    # Redessine complètement le graphe
    def draw_graphe(self):
        self.ax.clear()
        self.__draw_graphe()
        self.draw()

    # Dessin "privé" du graphe
    def __draw_graphe(self):
        if self.__controller.graphe() is None:
            return

        try:
            graphe = self.__controller.graphe()
            model = self.__controller._model

            # Préparer les couleurs des nœuds
            node_colors = []
            for node in graphe.nodes():
                if node == model.start_node:
                    node_colors.append('#4CAF50')  # Vert pour départ
                elif node == model.end_node:
                    node_colors.append('#F44336')  # Rouge pour arrivée
                elif node in model.visited_nodes:
                    node_colors.append('#9C27B0')  # Violet pour visités (parcours)
                elif node == model.selected_node:
                    node_colors.append('#FF9800')  # Orange pour sélectionné
                else:
                    node_colors.append('skyblue')  # Bleu par défaut

            # Dessin des noeuds et labels
            nx.draw_networkx_nodes(graphe, self._pos, node_color=node_colors,
                                   node_size=800, ax=self.ax)
            nx.draw_networkx_labels(graphe, self._pos, font_size=10, ax=self.ax)

            # Préparer les couleurs et largeurs des arêtes
            edge_colors = []
            edge_widths = []

            # Créer une liste d'arêtes du plus court chemin pour comparaison
            path_edges = []
            if len(model.shortest_path) > 1:
                for i in range(len(model.shortest_path) - 1):
                    path_edges.append((model.shortest_path[i], model.shortest_path[i + 1]))
                    path_edges.append((model.shortest_path[i + 1], model.shortest_path[i]))  # Les deux sens

            for edge in graphe.edges():
                # Arête fait partie du plus court chemin
                if edge in path_edges:
                    edge_colors.append('#4CAF50')  # Vert pour le chemin
                    edge_widths.append(4)
                # Arête sélectionnée
                elif self._selected_edge is not None and (
                        edge == self._selected_edge or edge == (self._selected_edge[1], self._selected_edge[0])):
                    edge_colors.append('#F44336')  # Rouge pour sélection
                    edge_widths.append(3)
                else:
                    edge_colors.append('black')
                    edge_widths.append(2)

            nx.draw_networkx_edges(graphe, self._pos, ax=self.ax,
                                   edge_color=edge_colors, width=edge_widths)

            # Afficher les poids des arêtes
            labels = nx.get_edge_attributes(graphe, "weight")
            nx.draw_networkx_edge_labels(graphe, self._pos, edge_labels=labels, ax=self.ax)

            # Zoom fixe
            self.ax.set_xlim(-1.5, 1.5)
            self.ax.set_ylim(-1.5, 1.5)

        except (NetworkXError, Exception) as e:
            print(f"Erreur draw: {e}")

    # Le modèle notifie que la position des noeuds a changé
    def on_graph_changed(self, position):
        self._pos = position
        self.draw_graphe()

    # Gestion clic souris
    def mousePressEvent(self, event):
        pos = self._convert_pos(event)

        if event.button() == Qt.MouseButton.LeftButton:
            # Essaye d'abord de cliquer un noeud
            clicked_node = self._find_node_at_position(pos)

            if clicked_node is not None:
                # Si en mode sélection de chemin, gérer différemment
                if self.__controller.path_mode:
                    self.__controller.select_path_node(clicked_node)
                else:
                    self.__controller._model.selected_node = clicked_node
                    self._selected_edge = None
                    self._dragging_node = clicked_node
                    self._drag_start_pos = pos
                    self.__controller.update_edge_ui(None)
                    self.draw_graphe()
            else:
                clicked_edge = self._find_edge_at_position(pos)
                if clicked_edge is not None:
                    self._selected_edge = clicked_edge
                    self.__controller._model.selected_node = None
                    self._dragging_node = None
                    self.draw_graphe()
                    self.__controller.update_edge_ui(clicked_edge)
                else:
                    self._selected_edge = None
                    self.__controller._model.selected_node = None
                    self.__controller.update_edge_ui(None)
                    # Ne pas ajouter de nœud en mode chemin
                    if not self.__controller.path_mode:
                        self.__controller._model.add_node(pos)

        elif event.button() == Qt.MouseButton.RightButton:
            # Début d'un drag pour créer une arête
            clicked_node = self._find_node_at_position(pos)
            if clicked_node is not None:
                self._dragging_node = clicked_node
                self._drag_start_pos = pos

    # Gestion déplacement souris (drag de noeud)
    def mouseMoveEvent(self, event):
        if self._dragging_node is None:
            return

        pos = self._convert_pos(event)
        if event.buttons() == Qt.MouseButton.LeftButton:

            if self._drag_start_pos is not None:
                movement = np.linalg.norm(np.array(pos) - np.array(self._drag_start_pos))

                # Threshold pour éviter les micro-déplacements
                if movement > self._drag_threshold / 100:
                    self.__controller._model.move_node(self._dragging_node, pos)

    # Relâchement bouton souris
    def mouseReleaseEvent(self, event):
        if self._dragging_node is None:
            return

        pos = self._convert_pos(event)

        # Clic droit relâché = tentative de création d'arête
        if event.button() == Qt.MouseButton.RightButton:
            target_node = self._find_node_at_position(pos)

            if target_node is not None and target_node != self._dragging_node:
                # Ajout d'une arête (poids par défaut = 1)
                self.__controller._model.add_edge(self._dragging_node, target_node, weight=1)

            # Reset drag
            self._dragging_node = None
            self._drag_start_pos = None

    # Gestion des touches clavier
    def keyPressEvent(self, event):
        model = self.__controller._model

        if event.key() == Qt.Key.Key_Delete:
            if self._selected_edge is not None:
                model.delete_edge(self._selected_edge)
                self._selected_edge = None
                self.__controller.update_edge_ui(None)
            elif model.selected_node is not None:
                model.delete_node(model.selected_node)

        elif event.key() == Qt.Key.Key_P:
            # Lancer le parcours avec la touche P
            self.__controller.start_traversal()