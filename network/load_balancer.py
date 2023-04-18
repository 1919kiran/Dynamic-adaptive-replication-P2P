import math
import random
import threading
import json
import pika
import sys
from multiprocessing import Manager
from network.node import Node


class LoadBalancer(threading.Thread):
    def __init__(self, num_nodes, num_files):
        try:
            super().__init__()
            self.connection = None
            self.channel = None
            self.num_nodes = num_nodes
            self.num_files = num_files
            self.nodes = []
            self.file_mapping = dict()
            self.node_mapping = dict()
            self.node_locations = dict()
            self.node_pool = dict()
            self.ohs_map = Manager().dict()  # dictionary of node to ohs
            self.adj_list = Manager().dict()  # dictionary of node to set of nodes
        except Exception as e:
            print("Error while initializing the load balancer")

    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        print("Load balancer has started and connected to message queue...")
        queue_name = "job_queue"
        self.channel.queue_declare(queue=queue_name)
        self.channel.queue_bind(queue=queue_name, exchange="amq.direct", routing_key=queue_name)
        self.channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=self.callback)
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        request_body = json.loads(body.decode())
        file_id = request_body["file_id"]
        node_id = self.get_nearby_node(file_id=request_body["file_id"], request_origin=request_body["origin"])
        # print(f"File mapping for file{file_id}: {self.file_mapping.get(file_id)}")
        if node_id is not None:
            node_pid = self.node_pool.get(node_id)
            node = next((n for n in self.nodes if n.pid == node_pid), None)
            if node is not None:
                node.enqueue_request(request_body)
            # print(f"Nearby node for file{request_body['file_id']} at {request_body['origin']} is Node{node_id}")

    def get_nearby_node(self, file_id, request_origin):
        min_distance = sys.maxsize
        if self.file_mapping.get(file_id) is None:
            return None
        nearby_node = None
        for node_id in self.file_mapping.get(file_id):
            node_location = self.node_locations.get(node_id)
            node_origin_distance = compute_distance(request_origin, node_location)
            if node_origin_distance < min_distance:
                min_distance = node_origin_distance
                nearby_node = node_id
        return nearby_node

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
            3: [1, 2, 3, 4, 5]
        }
        for key, values in self.file_mapping.items():
            for value in values:
                self.node_mapping.setdefault(value, []).append(key)
        print("File mapping and node mapping is created")
        print(self.file_mapping)
        print(self.node_mapping)
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
                        fileset=fileset,
                        ohs_map=self.ohs_map,
                        adj_list=self.adj_list
                        )
            self.nodes.append(node)
        for node in self.nodes:
            node.start()
        i = 1
        for node in self.nodes:
            self.node_pool[i] = node.pid
            i += 1
        print("Node pool: ", self.node_pool)


def compute_distance(loc1, loc2):
    return math.sqrt((loc2[0] - loc1[0]) ** 2 + (loc2[1] - loc1[1]) ** 2)
