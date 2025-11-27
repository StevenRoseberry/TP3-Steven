from model.graphe_model import GrapheModel
from view.GrapheCanvas import GraphCanvas
from view.MainWindow import MainWindow
from workers import ShortestPathWorker, TraversalWorker

#Je suis pas certain si mon implémentation des workers est bonne..

# Contrôleur principal
class MainController:
    __view: MainWindow
    __model: GrapheModel
    __canvas: GraphCanvas
    __shortest_path_worker = None
    __traversal_worker = None
    __path_mode = False  # Mode sélection de départ/arrivée

    def __init__(self, view, model, canvas):
        self.__view = view
        self.__model = model
        self.__canvas = canvas

        # Connexions existantes
        self.__view.createButton.clicked.connect(self.generate_graph)
        self.__view.deleteButton.clicked.connect(self.delete_graph)
        self.__view.weightSpinBox.valueChanged.connect(self.apply_edge_weight)

        # Nouvelles connexions
        self.__view.findPathButton.clicked.connect(self.toggle_path_mode)
        self.__view.resetPathButton.clicked.connect(self.reset_path)

    def post_init(self):
        self.__model.grapheChanged.connect(self.__canvas.on_graph_changed)
        self.__model.grapheChanged.emit(self.__model.pos)

    def graphe(self):
        return self.__model.graphe

    @property
    def _model(self):
        return self.__model

    @property
    def path_mode(self):
        return self.__path_mode

    def generate_graph(self):
        self.__model.generate_graph()
        self.reset_path()
        self.__model.reset_traversal()

    def delete_graph(self):
        self.__model.delete_graph()
        self.reset_path()

    def update_edge_ui(self, selected_edge=None):
        edge = selected_edge if selected_edge is not None else self.__canvas._selected_edge

        if edge is None:
            self.__view.edgeLabel.setStyleSheet(
                "color: #999; font-style: italic; font-size: 14px;"
            )
            self.__view.edgeLabel.setText("Aucune sélection")
            self.__view.weightSpinBox.setEnabled(False)
            self.__view.weightSpinBox.blockSignals(True)
            self.__view.weightSpinBox.setValue(1)
            self.__view.weightSpinBox.blockSignals(False)
        else:
            weight = self.__model.get_edge_weight(edge)
            self.__view.edgeLabel.setText(f"{edge[0]} ↔ {edge[1]}")
            self.__view.edgeLabel.setStyleSheet(
                "color: #2196F3; font-size: 16px; font-weight: bold;"
            )
            self.__view.weightSpinBox.setEnabled(True)
            self.__view.weightSpinBox.blockSignals(True)
            self.__view.weightSpinBox.setValue(weight if weight else 1)
            self.__view.weightSpinBox.blockSignals(False)

    def apply_edge_weight(self):
        if self.__canvas._selected_edge is None:
            return

        new_weight = self.__view.weightSpinBox.value()
        self.__model.set_edge_weight(self.__canvas._selected_edge, new_weight)
        self.__canvas.draw_graphe()

    def toggle_path_mode(self):
        self.__path_mode = not self.__path_mode

        if self.__path_mode:
            self.__view.findPathButton.setText("Annuler sélection")
            self.__view.pathStatusLabel.setText("Sélectionnez le sommet de départ")
            self.__view.pathStatusLabel.setStyleSheet("color: #FF9800; font-weight: bold;")
            # Réinitialiser les sélections
            self.__model.start_node = None
            self.__model.end_node = None
            self.__model.shortest_path = []
        else:
            self.__view.findPathButton.setText("Trouver chemin")
            self.__view.pathStatusLabel.setText("")
            self.__model.start_node = None
            self.__model.end_node = None
            self.__model.shortest_path = []
            self.__canvas.draw_graphe()

    def select_path_node(self, node):
        if not self.__path_mode:
            return

        if self.__model.start_node is None:
            # Sélection du nœud de départ
            self.__model.start_node = node
            self.__view.pathStatusLabel.setText(f"Départ: {node} | Sélectionnez l'arrivée")
            self.__view.pathStatusLabel.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.__canvas.draw_graphe()
        elif self.__model.end_node is None:
            # Sélection du nœud d'arrivée
            if node == self.__model.start_node:
                self.__view.pathStatusLabel.setText(f"Départ: {self.__model.start_node} | Choisissez un autre sommet!")
                self.__view.pathStatusLabel.setStyleSheet("color: #F44336; font-weight: bold;")
                return

            self.__model.end_node = node
            self.__view.pathStatusLabel.setText(f"Recherche du chemin: {self.__model.start_node} → {node}...")
            self.__view.pathStatusLabel.setStyleSheet("color: #2196F3; font-weight: bold;")

            # Lancer la recherche dans un thread
            self.start_shortest_path_search()

    def start_shortest_path_search(self):
        # Afficher la progress bar indéterminée
        self.__view.pathProgressBar.setVisible(True)
        self.__view.pathProgressBar.setRange(0, 0)  # Mode indéterminé

        # Créer et lancer le worker
        self.__shortest_path_worker = ShortestPathWorker(self.__model)
        self.__shortest_path_worker.pathFound.connect(self.on_path_found)
        self.__shortest_path_worker.finished.connect(self.on_path_search_finished)
        self.__shortest_path_worker.start()

    def on_path_found(self, path):
        self.__model.shortest_path = path

        if len(path) > 0:
            distance = self.calculate_path_distance(path)
            self.__view.pathStatusLabel.setText(
                f"Chemin trouvé: {' → '.join(map(str, path))} | Distance: {distance:.2f}"
            )
            self.__view.pathStatusLabel.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.__view.pathStatusLabel.setText("Aucun chemin trouvé entre ces sommets")
            self.__view.pathStatusLabel.setStyleSheet("color: #F44336; font-weight: bold;")

        self.__canvas.draw_graphe()

    def on_path_search_finished(self):
        self.__view.pathProgressBar.setVisible(False)
        self.__path_mode = False
        self.__view.findPathButton.setText("Trouver chemin")

    def calculate_path_distance(self, path):
        total = 0
        for i in range(len(path) - 1):
            weight = self.__model.get_edge_weight((path[i], path[i + 1]))
            if weight:
                total += weight
        return total

    def reset_path(self):
        self.__model.reset_path()
        self.__path_mode = False
        self.__view.findPathButton.setText("Trouver chemin")
        self.__view.pathStatusLabel.setText("")
        self.__view.pathProgressBar.setVisible(False)
        self.__canvas.draw_graphe()

    def start_traversal(self):
        if self.__model.graphe.number_of_nodes() == 0:
            return

        # Réinitialiser le parcours précédent
        self.__model.reset_traversal()

        # Afficher la progress bar déterminée
        self.__view.traversalProgressBar.setVisible(True)
        self.__view.traversalProgressBar.setRange(0, 100)
        self.__view.traversalProgressBar.setValue(0)
        self.__view.traversalStatusLabel.setText("Parcours en cours...")
        self.__view.traversalStatusLabel.setStyleSheet("color: #2196F3; font-weight: bold;")

        # Créer et lancer le worker
        self.__traversal_worker = TraversalWorker(self.__model)
        self.__traversal_worker.nodeVisited.connect(self.on_node_visited)
        self.__traversal_worker.progressUpdated.connect(self.on_traversal_progress)
        self.__traversal_worker.finished.connect(self.on_traversal_finished)
        self.__traversal_worker.start()

    def on_node_visited(self, node):
        visited = self.__model.visited_nodes.copy()
        visited.append(node)
        self.__model.visited_nodes = visited

    def on_traversal_progress(self, progress):
        self.__view.traversalProgressBar.setValue(progress)

    def on_traversal_finished(self):
        self.__view.traversalStatusLabel.setText("Parcours terminé!")
        self.__view.traversalStatusLabel.setStyleSheet("color: #4CAF50; font-weight: bold;")

        # Cacher la progress bar après 2 secondes
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.hide_traversal_ui)

    def hide_traversal_ui(self):
        self.__view.traversalProgressBar.setVisible(False)
        self.__view.traversalStatusLabel.setText("")
        self.__model.reset_traversal()