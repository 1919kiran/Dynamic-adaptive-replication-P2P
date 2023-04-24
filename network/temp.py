import multiprocessing as mp
import random
import time

# Define the data transfer process
def data_transfer(src, dest):
    data_size = random.randint(100, 1000)  # bytes
    transfer_time = random.uniform(0.1, 1.0)  # seconds
    time.sleep(transfer_time)  # simulate transfer time
    bandwidth = data_size / transfer_time  # calculate bandwidth
    print(f"Node {src} to Node {dest}: Bandwidth = {bandwidth} bytes/second")

# Define the network topology
nodes = [mp.Process(target=data_transfer, args=(i, j)) for i in range(10) for j in range(i+1, 10)]

# Start the processes
for node in nodes:
    node.start()

# Wait for the processes to finish
for node in nodes:
    node.join()
