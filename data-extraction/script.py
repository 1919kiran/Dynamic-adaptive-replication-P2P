# import random
#
#
# def create_adjacency_list(num_nodes):
#     adj_list = {i: set() for i in range(1, num_nodes + 1)}
#     for curr in range(1, num_nodes):
#         num_neighbors = random.randint(1, num_nodes)
#         for i in range(num_neighbors):
#             neighbor = random.randint(1, num_nodes)
#             if curr != neighbor:
#                 adj_list[curr].add(neighbor)
#                 adj_list[neighbor].add(curr)
#     print("Created adjacency list")
#     for node_id, neighbors in adj_list.items():
#         print(f"Node{node_id} is connected to nodes {neighbors}")
#
#
# var = {
#     1: {2, 3, 4, 5},
#     2: {1, 4},
#     3: {1, 4, 5},
#     4: {2, 3},
#     5: {1, 3}
# }
#
# create_adjacency_list(5)

import datetime
import time

t1 = datetime.datetime.now()
time.sleep(1)
un = 0
un += datetime.datetime.now() - t1
print(un)