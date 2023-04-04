from network.manager import Manager
# from weight_calculator import WeightCalculator

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    # weight_calculator = WeightCalculator()
    # weight_calculator.start()
    manager = Manager(num_nodes=5, num_files=10)
    manager.create_adjacency_list()
    manager.create_file_mapping()
    manager.start()
    manager.send_requests()
    manager.wait()
    # manager.stop()
    manager.wait_until_done()




