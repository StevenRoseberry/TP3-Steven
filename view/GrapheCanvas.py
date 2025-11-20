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

    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        super().__init__(self.fig)
        if TYPE_CHECKING:
            self.__controller: MainController | None = None
        self.setFocus()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_controller(self, controller):
        self.__controller = controller

    def _convert_pos(self, event):
        x_fig, y_fig = self.mouseEventCoords(event)
        return self.ax.transData.inverted().transform((x_fig, y_fig))

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
                if distance < min_distance and distance < radius:
                    min_distance = distance
                    closest_node = node

        return closest_node

    def draw_graphe(self):
        self.ax.clear()
        self.__draw_graphe()
        self.draw()

    def __draw_graphe(self):
        if self.__controller.graphe() is None:
            return
        try:
            graphe = self.__controller.graphe()
            node_colors = []
            for node in graphe.nodes():
                if node == self.__controller._model.selected_node:
                    node_colors.append('red')
                else:
                    node_colors.append('skyblue')

            nx.draw_networkx_nodes(graphe, self._pos, node_color=node_colors, node_size=800, ax=self.ax)
            nx.draw_networkx_labels(graphe, self._pos, font_size=10, ax=self.ax)
            nx.draw_networkx_edges(graphe, self._pos, ax=self.ax)
            labels = nx.get_edge_attributes(graphe, "weight")
            nx.draw_networkx_edge_labels(graphe, self._pos, edge_labels=labels, ax=self.ax)

            self.ax.set_xlim(-1.5, 1.5)
            self.ax.set_ylim(-1.5, 1.5)
        except (NetworkXError, Exception) as e:
            print(f"Erreur draw: {e}")

    def on_graph_changed(self, position):
        self._pos = position
        self.draw_graphe()

    def mousePressEvent(self, event):
        pos = self._convert_pos(event)
        if event.button() == Qt.MouseButton.LeftButton:
            clicked_node = self._find_node_at_position(pos)
            if clicked_node is not None:
                self.__controller._model.selected_node = clicked_node
                self._dragging_node = clicked_node
                self._drag_start_pos = pos
                self.draw_graphe()
            else:
                self.__controller._model.add_node(pos)
        elif event.button() == Qt.MouseButton.RightButton:
            clicked_node = self._find_node_at_position(pos)
            if clicked_node is not None:
                self._dragging_node = clicked_node
                self._drag_start_pos = pos

    def mouseMoveEvent(self, event):
        if self._dragging_node is None:
            return
        pos = self._convert_pos(event)
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._drag_start_pos is not None:
                movement = np.linalg.norm(np.array(pos) - np.array(self._drag_start_pos))
                if movement > self._drag_threshold / 100:
                    self.__controller._model.move_node(self._dragging_node, pos)

    def mouseReleaseEvent(self, event):
        if self._dragging_node is None:
            return
        pos = self._convert_pos(event)
        if event.button() == Qt.MouseButton.RightButton:
            target_node = self._find_node_at_position(pos)
            if target_node is not None and target_node != self._dragging_node:
                self.__controller._model.add_edge(self._dragging_node, target_node, weight=1)
            self._dragging_node = None
            self._drag_start_pos = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            model = self.__controller._model
            if model.selected_node is not None:
                model.delete_node(model.selected_node)