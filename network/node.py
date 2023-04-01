import time
import random
import csv
import queue
import threading
from itertools import repeat
from manager import Manager

filemap = None  # dictionary of files to nodes
ohsmap = None  # dictionary of node to ohs
node_arr = list()  # list of objects
adj_map = list()  # dictionary of node to set of nodes


class Request:
    def __init__(self, filename):
        self.timestamp = time.time()
        self.filename = filename

    def __str__(self):
        return f"Request filename: {self.filename} at timestamp: {self.timestamp}"


# Begin node class
class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.max_capacity = 10
        self.local_files_access_amount = 0
        self.request_amount = 0
        self.forwarding_bandwidth = 0
        self.theta = 0.3
        self.phi = 0.8
        self.alpha = 70
        self.eps = 100
        self.accesses = []
        self.tcp_connection = []
        self.tbdf_queue = []
        self.storage = {}
        self.request_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_requests)
        self.worker_thread.daemon = True  # Make the thread a daemon so it doesn't block program exit
        self.worker_thread.start()

    def _process_requests(self):
        while True:
            request = self.request_queue.get()
            print("Processing request: ", request)

    def __str__(self):
        return f"Node ID is {self.node_id}"

    def add_access(self, file_id, timestamp, frequency):
        self.accesses.append((file_id, timestamp, frequency))

    def calculate_weights(self):
        weights = {}
        current_time = time.time()
        for file_id, timestamp, frequency in self.accesses:
            time_diff = current_time - timestamp
            weight = frequency * pow(2, -time_diff / self.time_window)
            if file_id in weights:
                weights[file_id] += weight
            else:
                weights[file_id] = weight
        return weights

    def calculate_request_amount(self):
        self.request_amount = sum(self.local_files_access_amount.values()) + self.forwarding_bandwidth

    def calculate_node_load(self):
        self.request_amount = self.local_files_access_amount + self.forwarding_bandwidth
        return self.request_amount / self.max_capacity

    def calculate_overheating_similarity(self):
        q1 = self.calculate_node_load()
        overheating_similarity = (q1 - self.theta) / (
                self.phi - self.theta) if self.theta <= q1 <= self.phi else 0 if q1 < self.theta else 1
        return overheating_similarity

    def overheating_similarity_membership(self, curr_ohs):
        beta = 1
        print("beta ", beta)
        ohs_member = 100 // (1 + (1 / beta * pow((curr_ohs - self.phi), 2)))
        print("ohs member", ohs_member)
        return 1 if self.alpha <= ohs_member else 0

    def accept_input(self, filename):
        self.request_queue.put(Request(filename))
        print("File Served", filename)  # background
        if filename in self.storage:
            self.storage[filename] += 1
        else:
            self.storage[filename] = 1
        self.tcp_connection.append(filename)
        self.local_files_access_amount += 1
        curr_ohs = self.calculate_overheating_similarity()
        print("curr ohs ", curr_ohs)
        ohsmap[self.node_id] = curr_ohs
        if (curr_ohs > self.phi):
            print("Node Overloaded")
            print("___________")
            return
        if self.overheating_similarity_membership(curr_ohs):
            self.create_replica()
        else:
            print("Replica creation not required")
            print("___________")

    def build_priority_queue(self):
        print("Creating replica")
        print("___________")

    def create_replica(self):
        self.build_priority_queue()


# End node class

def create_nodes(num):
    for i in range(num):
        node = Node(i)
        global node_arr
        node_arr.append(node)

    for i in node_arr:
        print(i)

    global ohsmap
    ohsmap = dict(zip(range(num), repeat(0)))
    print("ohsmap ", str(ohsmap))


def create_adjacencylist(num):
    adj_map = {i: set() for i in range(num)}
    for curr in range(num):
        num_neighbors = random.randint(1, num)
        for i in range(num_neighbors):
            neighbor = random.choice(range(num))
            if curr != neighbor:
                adj_map[curr].add(neighbor)
                adj_map[neighbor].add(curr)

    for node_id, neighbors in adj_map.items():
        print(f"Node {node_id} is connected to nodes {neighbors}")


def create_filemap():
    global filemap
    filemap = {
        'file1': [0, 6],
        'file2': [2, 3],
        'file3': [1, 4, 8]
    }
    print("File map is created")
    print(filemap)


# input starttime + delta: file_name
access_pattern = None


def send_requests():
    with open('input.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        start_time = time.time()
        for row in reader:
            delta = int(row['delta'])
            filename = row['filename']
            # time_diff = (time.time() - start_time)*1000
            # if delta <= time_diff:
            nodeid = select_node(filename)
            print("Request Sent")
            node_arr[nodeid].accept_input(filename)
            # else:
            #     time.sleep(1)


def select_node(filename):
    global filemap
    nodes = filemap.get(filename)
    print("Nodes for the file", nodes)
    min_ohs = 1
    node_id = None
    global ohsmap
    for node in nodes:
        ohs_node = ohsmap.get(node)
        if ohs_node < min_ohs:
            min_ohs = ohs_node
            node_id = node
    return node_id


create_nodes(10)
create_adjacencylist(10)
create_filemap()

send_requests()
