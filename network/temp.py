# import csv
# import datetime
# import time
#
# from apscheduler.schedulers.background import BackgroundScheduler
#
# x = 1
#
# # define a function to send the request
# def send_request():
#     # do something with the response
#     global x
#     print("x=", x)
#     x += 1
#
#
# # read the timestamps from the CSV file
# timestamps = [time.time()]
#
# # create a scheduler object
# scheduler = BackgroundScheduler()
#
# # iterate over the timestamps and schedule a request at each one
# for timestamp in timestamps:
#     # convert the timestamp to a datetime object
#     request_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
#
#     # schedule the request to be sent at the specified timestamp
#     scheduler.add_job(send_request, 'date', run_date=request_time)
#
# # start the scheduler
# scheduler.start()


# overheating = [40, 3, 18, 21, 10]
# degree = [1, 2, 2, 3, 3]
#
# matrix = list(list())
#
#
# def r(i, j):
#     return overheating[i] * degree[i] + overheating[j] * degree[j]
#
#
# matrix = [[0 for j in range(5)] for i in range(5)]
#
#
# for i in range(5):
#     for j in range(5):
#         if i == j:
#             matrix[i][j] = 1
#         else:
#             matrix[i][j] = r(i, j)
#
#
# for i in range(5):
#     for j in range(5):
#         print(matrix[i][j], end=" ")
#     print()


import math

# sample data for 10 nodes with arbitrary values
nodes = [
    {"lat": 30.2672, "lon": -97.7431, "overheat": 0.3, "degree": 4},
    {"lat": 29.7604, "lon": -95.3698, "overheat": 0.6, "degree": 5},
    {"lat": 37.7749, "lon": -122.4194, "overheat": 0.1, "degree": 3},
    {"lat": 40.7128, "lon": -74.0060, "overheat": 0.8, "degree": 2},
    {"lat": 34.0522, "lon": -118.2437, "overheat": 0.5, "degree": 7},
    {"lat": 42.3601, "lon": -71.0589, "overheat": 0.2, "degree": 6},
    {"lat": 39.9526, "lon": -75.1652, "overheat": 0.4, "degree": 1},
    {"lat": 41.8781, "lon": -87.6298, "overheat": 0.7, "degree": 4},
    {"lat": 36.1699, "lon": -115.1398, "overheat": 0.9, "degree": 5},
    {"lat": 33.4484, "lon": -112.0740, "overheat": 0.2, "degree": 3}
]

# normalize the data
max_overheat = max(node["overheat"] for node in nodes)
max_degree = max(node["degree"] for node in nodes)

for node in nodes:
    node["overheat"] /= max_overheat
    node["degree"] /= max_degree

# function to calculate distance between two nodes using Haversine formula
def distance(node1, node2):
    R = 6371  # radius of Earth in kilometers
    lat1, lon1 = node1["lat"], node1["lon"]
    lat2, lon2 = node2["lat"], node2["lon"]
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

distances = []
for node in nodes:
    dist = distance(node, nodes[0])
    distances.append(dist)

max_dist = max(distances)
distances = [dist/max(distances) for dist in distances]

# function to calculate weighted score for a neighbor
def score(node, neighbor):
    dist = distance(node, neighbor)
    overheat = 1 - neighbor["overheat"]
    degree = neighbor["degree"]
    return overheat + 1 / dist + degree


# find the best neighbor for a given node
def best_neighbor(node, nodes):
    best_score = float("inf")
    best_neighbor = None
    for neighbor in nodes:
        if neighbor != node:
            curr_score = score(node, neighbor)
            if curr_score < best_score:
                best_score = curr_score
                best_neighbor = neighbor
    return best_neighbor


# # example usage: find the best neighbor for the first node
# print(distances)
#
# s = {"lat": 30.2672, "lon": -97.7431, "overheat": 0.3, "degree": 4}
# print(s.values())


nodes_ohs= [0.5128205128205129, 1.0, 0.0, 0.06666666666666674, 0.0]
nodes_degree= [1.0, 0.6666666666666666, 0.3333333333333333, 0.3333333333333333, 0.3333333333333333]
nodes_dist= [1.0, 0.0, 0.64625464643152, 0.9380231107920817, 0.3978304773483206]

nodes_ohs= [0.5083333333333334, 1.0, 0.0, 0.16666666666666669, 0.0]
nodes_degree= [1.0, 0.6666666666666666, 0.3333333333333333, 0.3333333333333333, 0.3333333333333333]
nodes_dist= [1.0, 0.0, 0.64625464643152, 0.9380231107920817, 0.3978304773483206]
scores = {}
best_score = float('-inf')
for (neighbor_id) in range(1,6):
    if 2 != neighbor_id:
        dist = nodes_dist[neighbor_id - 1]
        overheat = 1 - nodes_ohs[neighbor_id - 1]
        degree = nodes_degree[neighbor_id - 1]
        score = 0.75 * overheat + 0.15 * degree + 0.1 * dist
        scores[neighbor_id] = score
        curr_score = score
        if curr_score >= best_score:
            best_score = curr_score
            best_neighbor = neighbor_id
print("best_neighbor=", best_neighbor)
print(scores)