from network.manager import Manager
# from weight_calculator import WeightCalculator

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    # weight_calculator = WeightCalculator()
    # weight_calculator.start()
    manager = Manager(10)
    manager.create_adjacency_list()
    manager.create_file_mapping()
    manager.create_requests()
    manager.start()
    manager.wait()
    manager.stop()
    manager.wait_until_done()




