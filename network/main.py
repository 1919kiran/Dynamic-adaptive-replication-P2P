import time

from network.requests.location import get_node_locations
from network.network_manager import NetworkManager
from network.requests.request_generator import RequestGenerator

if __name__ == "__main__":
    num_nodes = 5
    num_files = 3

    request_generator = RequestGenerator(num_files=num_files)
    nw_manager = NetworkManager(num_nodes=num_nodes, num_files=num_files)

    adj_list = nw_manager.create_adjacency_list()
    file_mapping = nw_manager.create_file_mapping()
    node_locations = get_node_locations(num_nodes=num_nodes + 1)

    nw_manager.set_node_locations(node_locations)
    # nw_manager.delete_message_queues()
    nw_manager.create_message_queues()

    time.sleep(0.5)
    nw_manager.start_nodes()

    time.sleep(0.5)
    nw_manager.start()

    time.sleep(0.5)
    request_generator.start()

