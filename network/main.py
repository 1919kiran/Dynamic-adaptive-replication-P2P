import time
from network.request_generator import RequestGenerator
from network.load_balancer import NetworkManager
from network.node import Node
from location import get_node_locations


if __name__ == "__main__":
    num_nodes = 5
    num_files = 3
    redis_server_creds = {
        "host": "localhost",
        "port": 6379,
        "db": 0
    }

    request_generator = RequestGenerator(num_files=num_files)
    load_balancer = NetworkManager(num_nodes=num_nodes, num_files=num_files)

    adj_list = load_balancer.create_adjacency_list()
    file_mapping = load_balancer.create_file_mapping()
    node_locations = get_node_locations(num_nodes=num_nodes + 1)

    load_balancer.set_node_locations(node_locations)
    load_balancer.delete_message_queues()
    load_balancer.create_message_queues()

    time.sleep(1)
    load_balancer.start_nodes()
    time.sleep(1)
    load_balancer.start()
    time.sleep(1)
    request_generator.start()

