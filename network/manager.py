class Manager:
    def __init__(self, node_id):
        self.node_id = node_id
        self.neighbors = set()

    def add_neighbor(self, neighbor_id):
        self.neighbors.add(neighbor_id)

    def remove_neighbor(self, neighbor_id):
        self.neighbors.remove(neighbor_id)

    def get_neighbors(self):
        return self.neighbors