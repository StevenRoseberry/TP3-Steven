import time
from PyQt6.QtCore import QThread, pyqtSignal

# Aide de ClaudeAI pour l'implémentation
class ShortestPathWorker(QThread):
    pathFound = pyqtSignal(list)
    finished = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model

    def run(self):
        # Petit délai pour voir la progress bar
        time.sleep(0.5)

        # Calcul du plus court chemin
        path = self.model.find_shortest_path()

        # Émettre le résultat
        self.pathFound.emit(path)
        self.finished.emit()


class TraversalWorker(QThread):
    nodeVisited = pyqtSignal(int)
    progressUpdated = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._is_running = True

    def run(self):
        nodes = list(self.model.graphe.nodes())
        total_nodes = len(nodes)

        for i, node in enumerate(nodes):
            if not self._is_running:
                break

            # Émettre le nœud visité
            self.nodeVisited.emit(node)

            # Mettre à jour la progress bar
            progress = int((i + 1) / total_nodes * 100)
            self.progressUpdated.emit(progress)

            # Pause d'une seconde entre chaque noeud
            time.sleep(1)

        self.finished.emit()

    def stop(self):
        self._is_running = False