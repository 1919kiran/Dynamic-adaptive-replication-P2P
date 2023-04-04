import threading

import csv
import datetime
import random
import time
import queue
from itertools import repeat
from network.node import Node
from celery import Celery


class Manager:
    def __init__(self, num_nodes, num_files):
        self.num_nodes = num_nodes
        self.num_files = num_files
        self.file_mapping = dict()
        self.ohsmap = None  # dictionary of node to ohs
        self.nodes = list()  # list of objects
        self.adj_list = dict()  # dictionary of node to set of nodes
        self.access_pattern = list()
        self.request_queue = queue.Queue()
        for i in range(self.num_nodes):
            node = Node(i, self.request_queue)
            self.nodes.append(node)

    def start(self):
        for node in self.nodes:
            node.start()

    def stop(self):
        for node in self.nodes:
            node.stop()

    def wait(self):
        self.request_queue.join()

    def send_requests(self):
        thread = threading.Thread(target=self.process_requests)
        thread.start()

    def process_requests(self):
        first_epoch = None
        second_epoch = None
        with open('../input/pattern.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(reader)
            for row in reader:
                if first_epoch is None:
                    first_epoch = datetime.datetime.strptime(str(row[0]), '%Y-%m-%d %H:%M:%S.%f')
                    continue
                # timestamp = 2023-04-01 23:00:34.636319
                if second_epoch is None:
                    second_epoch = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
                    delta = (second_epoch - first_epoch).total_seconds()
                self.access_pattern.append(int(row[1]))

        # files_access = {i: 0 for i in range(1, self.num_nodes + 1)}
        for i in self.access_pattern:
            # files = ""
            for f in range(i):
                random_file = random.randint(1, self.num_files)
                # files_access[random_file] += 1
                self.request_queue.put(random_file)
                # files = files + "," + str(random_file)
            # print("making requests for files: ", files, flush=True)
            time.sleep(0.1)

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
        self.adj_list = {i: set() for i in range(self.num_nodes)}
        for curr in range(self.num_nodes):
            num_neighbors = random.randint(1, self.num_nodes)
            for i in range(num_neighbors):
                neighbor = random.choice(range(self.num_nodes))
                if curr != neighbor:
                    self.adj_list[curr].add(neighbor)
                    self.adj_list[neighbor].add(curr)

        print("Created adjacency list")
        # for node_id, neighbors in self.adj_list.items():
        #     print(f"Node {node_id} is connected to nodes {neighbors}")

    def create_file_mapping(self):
        # self.file_mapping = {
        #     'file1': random.sample(range(1, self.num+1), random.randint(1, int(self.num/2))),
        #     'file2': random.sample(range(1, self.num+1), random.randint(1, int(self.num/2))),
        #     'file3': random.sample(range(1, self.num+1), random.randint(1, int(self.num/2)))
        # }
        for k in range(self.num_files):
            v = random.sample(range(1, self.num_nodes + 1), random.randint(1, int(self.num_nodes / 2)))
            self.file_mapping[k] = v
        print("File map is created")
        print(self.file_mapping)

    def select_node(self, filename):
        nodes = self.filemap.get(filename)
        print("Nodes for the file: ", nodes)
        min_ohs = 1
        node_id = None
        for node in nodes:
            ohs_node = self.ohsmap.get(node)
            if ohs_node < min_ohs:
                min_ohs = ohs_node
                node_id = node
        return node_id

