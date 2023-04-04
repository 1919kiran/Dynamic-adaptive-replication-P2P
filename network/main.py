import time

from network.manager import NetworkManager
from network.weight_calculator import WeightCalculator

# from weight_calculator import WeightCalculator

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    # weight_calculator = WeightCalculator()
    # weight_calculator.start()
    manager = NetworkManager(num_nodes=5, num_files=10)
    manager.create_adjacency_list()
    manager.create_file_mapping()
    time.sleep(1)
    manager.send_requests()
    manager.start_nodes()




