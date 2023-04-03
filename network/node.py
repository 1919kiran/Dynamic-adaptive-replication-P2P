import time
import random
import csv
import queue
import threading


# Begin node class
class Node(threading.Thread):
    def __init__(self, node_id, queue: queue.Queue):
        super().__init__()
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
        self.queue = queue

    def run(self):
        while True:
            item = self.queue.get()
            print("Node{} processing file{}".format(self.node_id, item))
            self.queue.task_done()

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
        # self.request_queue.put(Request(filename))
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
        if curr_ohs > self.phi:
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

