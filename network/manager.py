import csv
import datetime
import multiprocessing

import pika
import random
import threading
import time
from multiprocessing import Process, Manager
from network.node import Node


# from multiprocessing.managers import

class NetworkManager(threading.Thread):
    def __init__(self, num_nodes, num_files):
        self.connection = None
        self.num_nodes = num_nodes
        self.num_files = num_files
        self.file_mapping = dict()
        self.ohsmap = dict()  # dictionary of node to ohs
        self.nodes = list()  # list of objects
        self.adj_list = dict()  # dictionary of node to set of nodes
        self.access_pattern = list()
        try:
            super(NetworkManager, self).__init__()
        except Exception as e:
            print("Error while initializing manager")

    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        print("Manager connected to message queue")
        first_epoch = None
        second_epoch = None
        with open("../input/pattern.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            next(reader)
            for row in reader:
                if first_epoch is None:
                    first_epoch = datetime.datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M:%S.%f")
                    continue
                # timestamp = 2023-04-01 23:00:34.636319
                if second_epoch is None:
                    second_epoch = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
                    delta = (second_epoch - first_epoch).total_seconds()
                self.access_pattern.append(int(row[1]))

        for i in self.access_pattern:
            for f in range(i):
                file_number = random.randint(1, 3)
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
                channel = self.connection.channel()
                # q = f"queue_{file_number}"
                # print(q)
                channel.basic_publish(exchange="",
                                      routing_key=f"queue_{file_number}",
                                      body=str(file_number).encode())
            time.sleep(0.1)

    def create_message_queues(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = self.connection.channel()
        for key in self.file_mapping.keys():
            channel.queue_declare(queue=f"queue_{key}")
            print(f"Queue queue_{key} created successfully.")

    def delete_message_queues(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = self.connection.channel()
        for key in self.file_mapping.keys():
            channel.queue_delete(queue=f"hello{key}")
            # print(f"Queue queue_{key} deleted successfully.")

    def get_files_by_nodeid(self, node_id):
        filenames = set()
        for filename, nodes in self.file_mapping.items():
            # print(f"filename = {filename} node={nodes}")
            if node_id in nodes:
                filenames.add(filename)
        return filenames

    def start_nodes(self):
        # processes = [multiprocessing.Process(target=node.run) for node in self.nodes]
        # for process in processes:
        #     process.start()

        # while True:
        #     time.sleep(1)
        # # print(f"Master queue size : {self.request_queue.qsize()}")
        # if self.request_queue.empty():
        #     break
        for node in self.nodes:
            node.start()

    def send_requests(self):
        thread = threading.Thread(target=self.publish_to_queue)
        thread.start()

    def wait_until_done(self):
        print("waiting...")
        self.request_queue.join()

    def add_neighbor(self, neighbor_id):
        self.neighbors.add(neighbor_id)

    def remove_neighbor(self, neighbor_id):
        self.neighbors.remove(neighbor_id)

    def get_neighbors(self):
        return self.neighbors

    # Creates an adjacency list
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
            print(f"Node {node_id} is connected to nodes {neighbors}")

        return self.adj_list

    def create_file_mapping(self):
        # self.file_mapping = {
        #     1: {1, 2, 3},
        #     2: {4, 5},
        #     3: {1},
        #     4: {1, 4},
        #     5: {1, 5}
        # }
        self.file_mapping = {
            1: {1}
        }
        # for k in range(self.num_files):
        #     v = random.sample(range(1, self.num_nodes + 1), random.randint(1, int(self.num_nodes / 2)))
        #     self.file_mapping[k] = v
        print("File map is created")
        print(self.file_mapping)
        return self.file_mapping

    def select_node(self, filename):
        nodes = self.file_mapping.get(filename)
        print("Nodes for the file: ", nodes)
        min_ohs = 1
        node_id = None
        for node in nodes:
            ohs_node = self.ohsmap.get(node)
            if ohs_node < min_ohs:
                min_ohs = ohs_node
                node_id = node
        return node_id
