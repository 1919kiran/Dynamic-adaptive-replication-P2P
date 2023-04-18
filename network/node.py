import heapq
import multiprocessing
import os
import threading
import time
from multiprocessing import Process

import pika

from network.sharedqueue import SharedQueue


class Node(Process):
    def __init__(self, node_id, node_location, fileset, shared_dict):
        try:
            super().__init__()
            self.node_id = node_id
            self.node_location = node_location
            self.shared_dict = shared_dict
            self.fileset = fileset
            self.max_capacity = 500
            self.request_amount = 0
            self.forwarding_bandwidth = 0
            self.theta = 0.3
            self.phi = 0.8
            self.alpha = 70
            self.eps = 100
            self.curr_ohs = 0
            self.connection = None
            self.local_queue = SharedQueue()
            self.weight_pq = []
            self.file_metadata = {file: [] for file in self.fileset}
            self.weights = dict()
        except Exception as e:
            print(f"Error while initializing Node{node_id}")

    def run(self):
        print(f"Node{self.node_id} has started and ready to accept requests...")
        # puller_thread = threading.Thread(target=self.pull_from_queue)
        processor_thread = threading.Thread(target=self.dequeue_from_local_queue)
        background_thread = threading.Thread(target=self.background_calculations)
        # puller_thread.start()
        processor_thread.start()
        background_thread.start()

    def __str__(self):
        return f"(Node{self.node_id}, PID={self.pid})"

    def enqueue_request(self, request):
        self.local_queue.put(request)

    def dequeue_from_local_queue(self):
        while True:
            try:
                if not self.local_queue.empty():
                    request = self.local_queue.get()
                    # print(f"Node{self.node_id} received request {request}")
                    time.sleep(0.075)
            except Exception as e:
                print(f"Error occurred in node{self.node_id}", e)

    def get_heartbeat(self):
        return self.curr_ohs

    def background_calculations(self):
        while True:
            self.curr_ohs = self.calculate_overheating_similarity()
            self.calculate_weights()
            top_file = heapq.nlargest(1, self.weights.items(), key=lambda x: x[1])
            # print(f"Node{self.node_id} largest = {top_items}")
            # print(f"Node{self.node_id} weights = {self.weights}")
            # print(f"Node{self.node_id} file metadata = {self.file_metadata}")
            # print(f"Node{self.node_id} access amount = {self.local_queue.qsize()}")
            # print(f"Node{self.node_id} node load = {self.calculate_node_load()}")
            # print(f"Node{self.node_id} ohs = {self.curr_ohs}")
            self.request_replication()
            self.shared_dict[self.node_id] = self.curr_ohs
            if self.node_id == 1:
                print("Node states: ", self.shared_dict)
            time.sleep(5)

    def calculate_weights(self):
        current_time = time.time()
        for file, timestamps in self.file_metadata.items():
            access_weight = 0
            for t in timestamps:
                time_diff = current_time - t
                access_weight += pow(2, -time_diff / 100)
            self.weights[file] = access_weight
            # self.add_to_priority_queue(file, access_weight)

    def calculate_node_load(self):
        self.request_amount = self.local_queue.qsize() + self.forwarding_bandwidth
        return self.request_amount / self.max_capacity

    def calculate_overheating_similarity(self):
        q1 = self.calculate_node_load()
        overheating_similarity = (q1 - self.theta) / (
                self.phi - self.theta) if self.theta <= q1 <= self.phi else 0 if q1 < self.theta else 1
        self.curr_ohs = overheating_similarity
        return overheating_similarity

    def overheating_similarity_membership(self, curr_ohs):
        beta = 1
        print("beta ", beta)
        ohs_member = 100 // (1 + (1 / beta * pow((curr_ohs - self.phi), 2)))
        print("ohs member", ohs_member)
        return 1 if self.alpha <= ohs_member else 0

    def accept_input(self, filename):
        # self.request_queue.put(Request(filename))
        # print("File Served", filename)  # background
        # if filename in self.storage:
        #     self.storage[filename] += 1
        # else:
        #     self.storage[filename] = 1
        # self.tcp_connection.append(filename)
        # self.local_files_access_amount += 1
        curr_ohs = self.calculate_overheating_similarity()
        print("curr ohs ", curr_ohs)
        if curr_ohs > self.phi:
            print("Node Overloaded")
            print("___________")
        if self.overheating_similarity_membership(curr_ohs):
            self.create_replica()
        else:
            pass
            # print("Replica creation not required")
            # print("___________")

    def add_request(self):
        pass

    # def add_to_priority_queue(self, filename, weight):
    #     # self.weight_pq.put((weight, filename))
    #     for file, weight in self.weights.items():
    #         if
    #         # print("(file, weight) = ", file, " ", weight)
    #         heapq.heappush(self.weight_pq, (file, weight))
    #     # print("___________")

    def create_replica(self, fild_id):
        print("Replica created")

    def request_replication(self):
        pass

    def get_neighbours(self):
        pass


