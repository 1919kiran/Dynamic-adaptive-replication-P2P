import json
import random
import threading
import time
from multiprocessing import Manager

import pika

from cython_modules import distance_calculator
from network.node import Node
from network.util.util import normalize


class NetworkManager(threading.Thread):
    def __init__(self, num_nodes, num_files):
        try:
            super().__init__()
            self._shared_memory = Manager()
            self.connection = None
            self.channel = None
            self.num_nodes = num_nodes
            self.num_files = num_files
            self.nodes = []
            self.file_mapping = self._shared_memory.dict()
            self.node_mapping = self._shared_memory.dict()
            self.node_locations = self._shared_memory.dict()
            self.node_pool = self._shared_memory.dict()
            self.acceptance_state = self._shared_memory.dict()
            self.ohs_map = self._shared_memory.dict()  # dictionary of node to ohs
            self.adj_list = self._shared_memory.dict()  # dictionary of node to set of nodes
        except Exception as e:
            print("Error while initializing the network manager")

    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        print("Network manager has started and connected to message queue...")
        queue_name = "job_queue"
        self.channel.queue_declare(queue=queue_name)
        self.channel.queue_bind(queue=queue_name, exchange="amq.direct", routing_key=queue_name)
        self.channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=self.callback)
        self.channel.start_consuming()
        # background_process = threading.Thread(target=self.background_process)
        # background_process.start()

    def callback(self, ch, method, properties, body):
        # print(self.file_mapping)
        request_body = json.loads(body.decode())
        file_id = request_body["file_id"]
        node_ids = self.get_ordered_nodes(file_id=request_body["file_id"], request_origin=request_body["origin"])
        i = 0
        for node_id in node_ids:
            i += 1
            node_pid = self.node_pool.get(node_id)
            # node = next((n for n in self.nodes if n.pid == node_pid and self.acceptance_state[node_id]), None)
            node = None
            for n in self.nodes:
                if n.pid == node_pid and self.acceptance_state[node_id]:
                    node = n
            if node is not None:
                # print(f"Sending file{file_id} to Node{node_id}")
                node.enqueue_request(request_body)
                return
            elif i != len(node_ids):
                continue
            else:
                # print("node_ids = ", node_ids)
                print("All nodes are overloaded. Pausing for 5 secs")
                time.sleep(5)

            # print(f"Nearby node for file{request_body['file_id']} at {request_body['origin']} is Node{node_id}")

    def get_ordered_nodes(self, file_id, request_origin):
        if self.file_mapping.get(file_id) is None:
            return None

        node_distances = {}
        node_ohs = {}
        for node_id in self.file_mapping.get(file_id):
            node_location = self.node_locations.get(node_id)
            node_origin_distance = distance_calculator.euclidean_distance(request_origin[0], request_origin[1],
                                                                          node_location[0], node_location[1])
            node_distances[node_id] = node_origin_distance
            node_ohs[node_id] = self.ohs_map.get(node_id)

        normalized_distances = normalize(list(node_distances.values()))
        normalized_loads = normalize(list(node_ohs.values()))
        normalized_distance = {node: dist for node, dist in zip(node_distances.keys(), normalized_distances)}
        normalized_ohs_dict = {node: load for node, load in zip(node_ohs.keys(), normalized_loads)}

        def sorting_key(node):
            return normalized_distance[node] + normalized_ohs_dict[node]

        nodes = list(node_distances.keys())
        sorted_nodes = sorted(nodes, key=sorting_key)

        return sorted_nodes

    def create_message_queues(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = self.connection.channel()
        for key in self.file_mapping.keys():
            channel.queue_declare(queue="job_queue")
            print(f"Job Queue created successfully.")

    def delete_message_queues(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = self.connection.channel()
        channel.queue_delete(queue="job_queue")
        # print("Job Queue deleted successfully.")

    """ Returns a fileset of a node based on node_id """

    def get_files_by_nodeid(self, node_id):
        return self.node_mapping.get(node_id)

    """ Creates an adjacency list """
    def create_adjacency_list(self):
        self.adj_list = {i: set() for i in range(1, self.num_nodes + 1)}
        for curr in range(1, self.num_nodes):
            num_neighbors = random.randint(1, self.num_nodes)
            for i in range(num_neighbors):
                neighbor = random.randint(1, self.num_nodes)
                if curr != neighbor:
                    self.adj_list[curr].add(neighbor)
                    self.adj_list[neighbor].add(curr)
        print("Created adjacency list")
        for node_id, neighbors in self.adj_list.items():
            print(f"Node{node_id} is connected to nodes {neighbors}")

        return self.adj_list

    def set_node_locations(self, node_locations):
        i = 1
        for loc in node_locations:
            self.node_locations[i] = loc
            i += 1
        print(self.node_locations)

    def create_file_mapping(self):
        self.file_mapping = {
            1: [1, 2, 3],
            2: [1, 4, 5],
            3: [1, 4, 3]
        }
        for file_id, node_ids in self.file_mapping.items():
            for node_id in node_ids:
                if node_id not in self.node_mapping:
                    self.node_mapping[node_id] = []
                files = self.node_mapping[node_id]
                files.append(file_id)
                self.node_mapping[node_id] = files
        print("File mapping and node mapping is created")
        print("File to node mapping: ", self.file_mapping)
        print("Node to file mapping: ", self.node_mapping)
        return self.file_mapping

    def select_node(self, filename):
        nodes = self.file_mapping.get(filename)
        print("Nodes for the file: ", nodes)
        min_ohs = 1
        node_id = None
        for node in nodes:
            ohs_node = self.ohs_map.get(node)
            if ohs_node < min_ohs:
                min_ohs = ohs_node
                node_id = node
        return node_id

    def start_nodes(self):
        for i in range(1, self.num_nodes + 1):
            fileset = self.get_files_by_nodeid(i)
            node = Node(node_id=i,
                        node_locations=self.node_locations,
                        node_file_mapping=self.node_mapping,
                        file_node_mapping=self.file_mapping,
                        ohs_map=self.ohs_map,
                        adj_list=self.adj_list,
                        acceptance_state=self.acceptance_state
                        )
            self.nodes.append(node)
        for node in self.nodes:
            node.start()
        i = 1
        for node in self.nodes:
            self.acceptance_state[i] = True
            self.node_pool[i] = node.pid
            i += 1
        print("Node pool: ", self.node_pool)

    def background_process(self):
        while True:
            print("LB: ", self.file_mapping)
            time.sleep(5)
