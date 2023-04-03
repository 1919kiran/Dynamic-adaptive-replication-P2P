import csv
import datetime
import random
import threading
import queue
from itertools import repeat
from network.node import Node
from celery import Celery


class Manager:
    def __init__(self, num):
        self.num = num
        self.file_mapping = None
        self.filemap = None  # dictionary of files to nodes
        self.ohsmap = None  # dictionary of node to ohs
        self.nodes = list()  # list of objects
        self.adj_list = dict()  # dictionary of node to set of nodes
        self.access_pattern = list()
        self.request_queue = queue.Queue()
        for i in range(num):
            node = Node(i, self.request_queue)
            self.nodes.append(node)

    def start(self):
        for node in self.nodes:
            node.start()

    def stop(self):
        for node in self.nodes:
            node.join()

    def wait(self):
        self.request_queue.join()

    def create_requests(self):
        first_epoch = None
        second_epoch = None
        with open('../input/pattern.csv', newline='') as csvfile:
            # Create a CSV reader object
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

        # files_access = {i: 0 for i in range(1, self.num + 1)}
        for i in self.access_pattern:
            # files = ""
            # for f in range(t):
            #     random_file = random.randint(1, self.num)
            #     files_access[random_file] += 1
            #     files = files + "file {} ".format(random_file)
            # print("making requests for files: ", files)
            self.request_queue.put(random.randint(1, self.num))

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
        self.adj_list = {i: set() for i in range(self.num)}
        for curr in range(self.num):
            num_neighbors = random.randint(1, self.num)
            for i in range(num_neighbors):
                neighbor = random.choice(range(self.num))
                if curr != neighbor:
                    self.adj_list[curr].add(neighbor)
                    self.adj_list[neighbor].add(curr)

        print("Created adjacency list")
        # for node_id, neighbors in self.adj_list.items():
        #     print(f"Node {node_id} is connected to nodes {neighbors}")

    def create_file_mapping(self):
        self.file_mapping = {
            'file1': random.sample(range(1, self.num + 1), random.randint(1, self.num / 2)),
            'file2': random.sample(range(1, self.num + 1), random.randint(1, self.num / 2)),
            'file3': random.sample(range(1, self.num + 1), random.randint(1, self.num / 2))
        }
        print("File map is created")
        # print(self.file_mapping)

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

