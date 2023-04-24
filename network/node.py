import heapq
import threading
import time
from multiprocessing import Process
from cython_modules import distance_calculator
from network.sharedqueue import SharedQueue
from util import normalize


class Node(Process):
    def __init__(self, node_id, node_locations, node_file_mapping,
                 file_node_mapping, ohs_map, adj_list, acceptance_state):
        try:
            super().__init__()
            self.node_id = node_id
            self.node_locations = node_locations
            self.ohs_map = ohs_map
            self.adj_list = adj_list
            self.node_file_mapping = node_file_mapping
            self.file_node_mapping = file_node_mapping
            self.acceptance_state = acceptance_state
            self.max_capacity = 500
            self.request_amount = 0
            self.forwarding_bandwidth = 0
            self.available_bandwidth = 1000
            self.theta = 0.3
            self.phi = 0.7
            self.alpha = 70
            self.eps = 100
            self.curr_ohs = 0
            self.connection = None
            self.local_queue = SharedQueue()
            self.weight_pq = []
            self.file_set = self.node_file_mapping.get(self.node_id)
            self.file_metadata = {}
            if self.file_set is not None:
                for file in self.file_set:
                    self.file_metadata[file] = []
            self.weights = dict()
        except Exception as e:
            print(f"Error while initializing Node{node_id}", e)

    def run(self):
        print(f"Node{self.node_id} has started and ready to accept requests...")
        processor_thread = threading.Thread(target=self.dequeue_from_local_queue)
        background_thread = threading.Thread(target=self.background_calculations)
        processor_thread.start()
        background_thread.start()

    def __str__(self):
        return f"(Node{self.node_id}, PID={self.pid})"

    def dequeue_from_local_queue(self):
        """
        Simulates the processing of a request. This takes out elements from local queue for request processing.
        Also updates file metadata for the requested file.
        """
        while True:
            try:
                if not self.local_queue.empty():
                    request = self.local_queue.get()
                    file_id = int(request.get("file_id"))
                    if self.file_metadata.get(file_id) is not None:
                        file_accesses = self.file_metadata.get(file_id)
                        # Store the timestamp of request for this file (used for file weight calculation)
                        file_accesses.append(int(time.time()))
                        self.file_metadata[file_id] = file_accesses
                    time.sleep(0.075)
            except Exception as e:
                print(f"Error occurred in node{self.node_id}", e)

    def background_calculations(self):
        """
        Responsible for all background calculations such as:
        1. Node's overheating similarity.
        2. Weights of all files in the node.
        3. Available bandwidth and latency.
        4. Handling of replica creation opportune moment.
        5. Estimating the most optimal placement node once the opportune moment has arrived.
        6. Invoking file replication methods when the placement node is available for replication.
        """
        while True:
            self.curr_ohs = self.calculate_overheating_similarity()
            self.ohs_map[self.node_id] = self.curr_ohs
            self.calculate_weights()

            if self.node_id == 2:
                print("Node ohs: ", self.ohs_map)
                # print("Node acceptance state: ", self.acceptance_state)
                print("Queue size = ", self.local_queue.qsize())

            if self.curr_ohs >= self.phi:
                # Check if the node is overloaded. If yes, then get the hot file, calculate optimal placement node
                # and begin replication
                print(f"Creating replica for Node{self.node_id}...")
                hot_file = heapq.nlargest(1, self.weights.items(), key=lambda x: x[1])
                hot_file = hot_file[0][0]
                placement_nodes = self.get_optimal_neighbors(hot_file)
                if len(placement_nodes) == 0:
                    self.acceptance_state[self.node_id] = False
                    print(f"Cannot replicate File{hot_file} from Node{self.node_id} as there is no availability "
                          f"of nodes")
                for placement_node_id in placement_nodes:
                    self.start_replication(hot_file, placement_node_id)
                    self.update_mapping(placement_node_id, hot_file)
                    break
            elif self.curr_ohs < self.phi and self.acceptance_state[self.node_id] == False:
                # If the node is not overloaded and it's acceptance state was false, it implies now it is ready to
                # accept new requests.
                print(f"Node{self.node_id} is now ready to accept new requests...")
                self.acceptance_state[self.node_id] = True

            time.sleep(5)

    def enqueue_request(self, request):
        """
        Called by the network manager to directly put a request in node's local queue.
        """
        self.local_queue.put(request)

    def calculate_weights(self):
        """
        Calculates weight of each file based on TBDF by using the store request timestamps.
        """
        current_time = time.time()
        for file, timestamps in self.file_metadata.items():
            access_weight = 0
            for t in timestamps:
                time_diff = current_time - t
                access_weight += pow(2, -time_diff / 100)
            self.weights[file] = access_weight

    def calculate_node_load(self):
        self.request_amount = self.local_queue.qsize() + self.forwarding_bandwidth
        return self.request_amount / self.max_capacity

    def calculate_overheating_similarity(self):
        q1 = self.calculate_node_load()
        overheating_similarity = (q1 - self.theta) / (
                self.phi - self.theta) if self.theta <= q1 <= self.phi else 0 if q1 < self.theta else 1
        self.curr_ohs = overheating_similarity
        return overheating_similarity

    def overheating_similarity_membership(self):
        beta = 50
        ohs_member = 100 // (1 + ((self.curr_ohs - self.phi) * (self.curr_ohs - self.phi) * (beta)))
        if self.node_id == 2:
            print(f"ohs member {self.node_id}", ohs_member)
        return 1 if self.alpha <= ohs_member else 0

    def start_replication(self, file_id, placement_node_id):
        """
        Handles replication of the file from current node to the given placement node.
        """
        print(f"File transfer for File{file_id} is in progress from Node{self.node_id} to Node{placement_node_id}")
        time.sleep(1)

    def get_optimal_neighbors(self, file_id):
        """
        Calculates the optimal neighbor based on the decreasing order of priority:
        1. Node with the lowest overheating similarity.
        2. Node with the highest degree.
        3. Node that is nearest to current node.
        """
        nodes_ohs = self.ohs_map
        nodes_degree = {node_id: len(connections) for node_id, connections in self.adj_list.items()}
        nodes_dist = {}
        curr_location = self.node_locations.get(self.node_id)
        for node_id, location in sorted(self.node_locations.items()):
            dist = distance_calculator.haversine_distance(curr_location[0], curr_location[1],
                                                          location[0], location[1])
            nodes_dist[node_id] = dist

        normalized_ohs = normalize(list(nodes_ohs.values()))
        normalized_degree = normalize(list(nodes_degree.values()))
        normalized_dist = normalize(list(nodes_dist.values()))

        normalized_ohs_list = {node: ohs for node, ohs in zip(nodes_ohs.keys(), normalized_ohs)}
        normalized_degree_list = {node: degree for node, degree in zip(nodes_degree.keys(), normalized_degree)}
        normalized_dist_list = {node: dist for node, dist in zip(nodes_dist.keys(), normalized_dist)}

        def sorting_key(node):
            return 0.75*normalized_ohs_list[node] + 0.15*normalized_degree_list[node] + 0.1*normalized_dist_list[node]

        nodes = list(nodes_ohs.keys())
        sorted_nodes = sorted(nodes, key=sorting_key)
        for node_id in sorted_nodes:
            # Remove overloaded nodes and the nodes where file is already present
            if file_id in self.node_file_mapping.get(node_id) or self.ohs_map.get(node_id) >= self.phi:
                sorted_nodes.remove(node_id)
        print()

        return sorted_nodes

    def update_mapping(self, placement_node_id, file_id):
        """
        Updates the file-to-node mapping and node-to-file mapping
        """
        placement_node_files = self.node_file_mapping.get(placement_node_id)
        if file_id not in placement_node_files:
            placement_node_files.append(file_id)
        self.node_file_mapping[placement_node_id] = placement_node_files

        nodes = self.file_node_mapping.get(file_id)
        if placement_node_id not in nodes:
            nodes.append(placement_node_id)
        self.file_node_mapping[file_id] = nodes

        print(f"Node{self.node_id}: ", self.node_file_mapping)
        print(f"Updated the file and node mapping of Node{placement_node_id}")
