import datetime
import heapq
import sys
import threading
import time
from multiprocessing import Process
import json
import pika
import psutil
from cython_modules import distance_calculator
from network.sharedqueue import SharedQueue
from network.util.util import normalize


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
            self.max_capacity = 1000
            self.request_amount = 0
            self.forwarding_bandwidth = 0
            self.available_bandwidth = 10000
            self.curr_bandwidth = 0
            self.avg_latency = 0
            self.theta = 0.3
            self.phi = 0.7
            self.alpha = 70
            self.eps = 100
            self.curr_ohs = 0
            self.weight_pq = []
            self.file_set = self.node_file_mapping.get(self.node_id)
            self.file_metadata = {}
            self.connection = None
            self.channel = None
            self.local_queue = SharedQueue()
            self.t1 = None
            self.unavailable_time = 0
            self.curr_idle_start = time.time()
            self.simulation_start = time.time()
            self.overheating_start = None
            self.total_overheating_time = 0
            self.total_idle_time = 0
            self.idle_ticks = 0
            if self.file_set is not None:
                for file in self.file_set:
                    self.file_metadata[file] = ([], [])
            self.weights = dict()
            self.node_metrics = []
            self.curr_node_location = self.node_locations.get(self.node_id)
            self.properties = pika.BasicProperties(headers={"producer_tag": f"Node{self.node_id}"})

        except Exception as e:
            print(f"[node {self.node_id}] Error while initializing Node{node_id}", e)

    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        print(f"[node {self.node_id}] Node{self.node_id} has started and ready to accept requests...")
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
                    time_for_replication = 0.005
                    request = self.local_queue.get()
                    file_id = int(request.get("file_id"))
                    file_origin = request.get("origin")
                    if self.file_metadata.get(file_id) is not None:
                        file_meta = self.file_metadata.get(file_id)
                        file_accesses = file_meta[0]
                        file_latencies = file_meta[1]
                        # Store the timestamp of request for this file (used for file weight calculation)
                        file_accesses.append(int(time.time()))
                        self.file_metadata[file_id] = file_meta
                        # Calculate the latency of this file
                        latency = distance_calculator.round_trip_time(
                            file_origin[0], file_origin[1],
                            self.curr_node_location[0], self.curr_node_location[1]
                        )
                        file_latencies.append(latency + time_for_replication)
                        total_latency = latency + time_for_replication
                        msg = {
                            "file": file_id,
                            "node": self.node_id,
                            "latency": total_latency*1000,
                            "available_buffer": self.local_queue.qsize(),
                            "capacity": self.max_capacity,
                            "ohs": self.curr_ohs
                        }
                        self.node_metrics.append(msg)
                        # self.channel.basic_publish(exchange="",
                        #                            routing_key="results",
                        #                            body=msg)
                        file_meta = (file_accesses, file_latencies)
                        self.file_metadata[file_id] = file_meta
                    time.sleep(time_for_replication)
            except Exception as e:
                print(f"[node {self.node_id}] Error occurred in node{self.node_id}", e)

    def background_calculations(self):
        """
        Responsible for all background calculations such as:
        1. Node's overheating similarity.
        2. Weights of all files in the node.
        3. Available bandwidth and latency.
        4. Handling of replica creation opportune moment.
        5. Estimating the most optimal placement node once the opportune moment has arrived.
        6. Invoking file replication methods when the placement node is available for replication.
        7. Publishing the node metrics to message queue.
        """
        while True:
            self.curr_ohs = self.calculate_overheating_similarity()
            self.ohs_map[self.node_id] = self.curr_ohs
            self.calculate_weights()
            avg_latency = self.calculate_latency()
            bw = self.available_bandwidth - (self.local_queue.qsize() * 10)
            if bw < 0:
                bw = 0
            if self.local_queue.qsize() == 0:
                self.idle_ticks += 1
                if self.idle_ticks == 1:
                    self.curr_idle_start = time.time()
                if self.idle_ticks == 100:
                    end = time.time()
                    self.total_idle_time += end - self.curr_idle_start
                    print(f"[node {self.node_id}] idle time = {self.total_idle_time} secs")
                    timing = {
                        "total_idle_time": self.total_idle_time,
                        "simulation_time": end - self.simulation_start,
                        "downtime": self.unavailable_time,
                        "overheated_time": self.total_overheating_time,
                        "normal_time": end - self.simulation_start - (self.total_idle_time + self.unavailable_time + self.total_overheating_time)
                    }
                    time.sleep(1)
                    f1 = f"metrics_node{self.node_id}.txt"
                    f2 = f"timing_node{self.node_id}.txt"
                    with open(f"results/{f1}", "w") as f:
                        f.write(str(self.node_metrics))
                    with open(f"results/{f2}", "w") as f:
                        f.write(str(timing))
                    time.sleep(1)
                    print(f"Stopping node {self.node_id}")
                    sys.exit(0)
            else:
                if self.idle_ticks > 0:
                    self.total_idle_time += time.time() - self.curr_idle_start
                    self.curr_idle_start = time.time()
                self.idle_ticks = 0
            self.curr_bandwidth = bw
            self.avg_latency = avg_latency
            if self.node_id == 1:
                # print(f"[node {self.node_id}] Node ohs: ", self.ohs_map)
                # print(f"[node {self.node_id}] Queue size = {self.local_queue.qsize()}")
                # print(f"[node {self.node_id}] Avg latency = {avg_latency} ms")
                # print(f"[node {self.node_id}] Available bandwidth = {bw} Mb")
                # print(f"[node {self.node_id}] idle time = {self.total_idle_time} secs")
                # print(f"[node {self.node_id}] unavailable time = {self.unavailable_time} secs")
                # print(f"[node {self.node_id}] overheating time = {self.total_overheating_time} secs")
                print(f"[node {self.node_id}] total simulation time = {time.time() - self.simulation_start} secs")
                # print(f"[node {self.node_id}] ohs = {self.curr_ohs}")
                # print(f"[node {self.node_id}] overheating time = {self.total_overheating_time} secs")
                # print(f"[node {self.node_id}] overheating time = {self.total_overheating_time} secs")

                print()
            flag = True
            if self.curr_ohs >= self.phi:
                # Check if the node is overloaded. If yes, then get the hot file, calculate optimal placement node
                # and begin replication
                self.overheating_start = time.time()
                hot_file = heapq.nlargest(1, self.weights.items(), key=lambda x: x[1])
                hot_file = hot_file[0][0]
                placement_nodes = self.get_optimal_neighbors(hot_file)
                if len(placement_nodes) == 0:
                    self.acceptance_state[self.node_id] = False
                    self.t1 = datetime.datetime.now()
                    print(f"[node {self.node_id}] Cannot replicate File{hot_file} from Node{self.node_id} as there is no availability of nodes")
                for placement_node_id in placement_nodes:
                    self.start_replication(hot_file, placement_node_id)
                    # self.update_mapping(placement_node_id, hot_file)
                    break
            elif self.curr_ohs < self.phi and not self.acceptance_state[self.node_id]:
                # If the node is not overloaded and it's acceptance state was false, it implies now it is ready to accept new requests.
                print(f"[node {self.node_id}] Node{self.node_id} is now ready to accept new requests...")
                self.acceptance_state[self.node_id] = True
                self.unavailable_time += (datetime.datetime.now() - self.t1).total_seconds()
                flag = False
                if self.overheating_start is not None:
                    self.total_overheating_time += time.time() - self.overheating_start
                    self.overheating_start = None
            elif self.curr_ohs < self.phi and flag:
                if self.overheating_start is not None:
                    self.total_overheating_time += time.time() - self.overheating_start
                    self.overheating_start = None

            # publish the metrics to message queue
            self.publish_metrics()
            time.sleep(0.25)

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
        for file, file_meta in self.file_metadata.items():
            access_weight = 0
            timestamps = file_meta[0]
            for t in timestamps:
                time_diff = current_time - t
                access_weight += pow(2, -time_diff / 100)
            self.weights[file] = access_weight

    def calculate_latency(self):
        count = 0
        avg_latency = 0
        for file, file_meta in self.file_metadata.items():
            access_weight = 0
            latencies = file_meta[1]
            n = len(latencies)
            if n != 0:
                avg_latency += sum(latencies) / n
            count += 1
        if count != 0:
            return avg_latency / count
        else:
            return None

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
        # if self.node_id == 2:
        #     print(f"[node {self.node_id}] ohs member {self.node_id}", ohs_member)
        return 1 if self.alpha <= ohs_member else 0

    def start_replication(self, file_id, placement_node_id):
        """
        Handles replication of the file from current node to the given placement node.
        """
        print(
            f"[node {self.node_id}] File transfer for File{file_id} is in progress from Node{self.node_id} to Node{placement_node_id}")
        # time.sleep(1)

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
            return 0.75 * normalized_ohs_list[node] + 0.15 * normalized_degree_list[node] + 0.1 * normalized_dist_list[
                node]

        nodes = []
        for node_id, connections in self.adj_list.items():
            if self.file_not_present_in_placement_node(file_id, placement_node_id=node_id) and self.ohs_map.get(node_id) < self.phi and self.is_connected(node_id):
                nodes.append(node_id)
        # print(f"[node {self.node_id}] nodes = {nodes}")
        sorted_nodes = sorted(nodes, key=sorting_key)
        # print(f"[node {self.node_id}] sorted nodes before removing = {sorted_nodes}")
        # for node_id in sorted_nodes:
        #     # Remove overloaded nodes and the nodes where file is already present
        #     c1 = self.file_present_in_placement_node(file_id, placement_node_id=node_id)
        #     c2 = self.ohs_map.get(node_id) >= self.phi
        #     c3 = self.is_connected(node_id)
        #     if c1 or c2 or c3:
        #         sorted_nodes.remove(node_id)
        # print(f"[node {self.node_id}] sorted nodes = {sorted_nodes}")
        return sorted_nodes

    def update_mapping(self, placement_node_id, file_id):
        """
        Updates the file-to-node mapping and node-to-file mapping
        """
        print(f"[node {self.node_id}] Old file-node mapping: {self.file_node_mapping}")
        print(f"[node {self.node_id}] Old node-file mapping: {self.node_file_mapping}")
        placement_node_files = self.node_file_mapping.get(placement_node_id)
        print("placement_node_files = ", placement_node_files)
        if file_id not in placement_node_files:
            placement_node_files.append(file_id)
        self.node_file_mapping[placement_node_id] = placement_node_files

        nodes = self.file_node_mapping.get(file_id)
        if placement_node_id not in nodes:
            nodes.append(placement_node_id)
        self.file_node_mapping[file_id] = nodes
        print(f"[node {self.node_id}] New file-node mapping: {self.file_node_mapping}")
        print(f"[node {self.node_id}] New node-file mapping: {self.node_file_mapping}")
        # print(f"[node {self.node_id}] Updated the file and node mapping of Node{placement_node_id}. New file to node mapping is: {self.file_node_mapping}")

    def is_connected(self, placement_node_id):
        connections = self.adj_list.get(self.node_id)
        if placement_node_id in connections:
            return True
        else:
            return False

    def file_not_present_in_placement_node(self, file_id, placement_node_id):
        # print(f"[node {self.node_id}]  target node={placement_node_id} "
        #       f"and hotfile={file_id} and res = {file_id in self.node_file_mapping.get(placement_node_id)}")
        if placement_node_id in self.file_node_mapping.get(file_id):
            return False
        else:
            return True

    def publish_metrics(self):
        process = psutil.Process(self.pid)
        message_body = {
            "node_id": self.node_id,
            "ohs": self.curr_ohs,
            "bandwidth": self.curr_bandwidth,
            "avg_latency": self.avg_latency,
            "queue_size": self.local_queue.qsize(),
            "file_set": self.node_file_mapping.get(self.node_id),
            "unavailable_time": self.unavailable_time,
            "memory": process.memory_percent()
        }
        message = json.dumps(message_body).encode("utf-8")
        self.channel.basic_publish(exchange="",
                                   routing_key="metrics_queue",
                                   body=message)
        # with open("../data-extraction/latency-best.txt", "r") as f:
        #     f.write(json.dumps(self.file_metadata))

