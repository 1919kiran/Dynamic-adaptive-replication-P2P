import time
from network.request_generator import RequestGenerator
from network.network_manager import NetworkManager
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
    nw_manager = NetworkManager(num_nodes=num_nodes, num_files=num_files)

    adj_list = nw_manager.create_adjacency_list()
    file_mapping = nw_manager.create_file_mapping()
    node_locations = get_node_locations(num_nodes=num_nodes + 1)

    nw_manager.set_node_locations(node_locations)
    nw_manager.delete_message_queues()
    nw_manager.create_message_queues()

    time.sleep(1)
    nw_manager.start_nodes()
    time.sleep(1)
    nw_manager.start()
    time.sleep(1)
    request_generator.start()

