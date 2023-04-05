import time
from network.manager import NetworkManager
from network.node import Node
import redis
from network.weight_calculator import WeightCalculator

# from weight_calculator import WeightCalculator

if __name__ == "__main__":
    # weight_calculator = WeightCalculator()
    # weight_calculator.start()

    num_nodes = 5
    num_files = 3

    redis_server_creds = {
        "host": "localhost",
        "port": 6379,
        "db": 0
    }

    manager = NetworkManager(num_nodes=num_nodes, num_files=num_files)
    adj_list = manager.create_adjacency_list()
    file_mapping = manager.create_file_mapping()
    # manager.delete_message_queues()
    manager.create_message_queues()

    nodes = []
    for i in range(1, num_nodes + 1):
        fileset = manager.get_files_by_nodeid(i)
        node = Node(node_id=i, fileset=fileset)
        nodes.append(node)

    time.sleep(1)

    manager.start()
    for node in nodes:
        node.start()

    # manager.send_requests()
    # manager.start_nodes()
