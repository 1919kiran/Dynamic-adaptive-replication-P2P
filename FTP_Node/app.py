from flask import (
    Flask, 
    jsonify,
    request
)
import numpy as np
import requests
import random
from sklearn.cluster import KMeans
app = Flask(__name__)

file_to_node = {}
node_to_IP = {}

access_amount_local = 0
forwarding_amount = 0
max_capacity = 100

theta = 0.3
phi = 0.8

@app.route('/requestfile',methods=["GET","POST"])
def index():    
    # return "file"
    # return calculate_overheating_similarity(0.45,[0.3, 0.4, 0.5, 0.6, 0.7])
    ohs = calculate_overheating_similarity_2(0.45,[0.3, 0.4, 0.5, 0.6, 0.7])
    print(ohs)
    return str(ohs)
    # send_file_to_peer(file_path, other_node_loads, ohs)

def calculate_overheating_similarity(q1, loads, k=3):
    # --Normalize the node load and other loads using min-max scaling
    min_load = min([min(loads), q1])
    max_load = max([max(loads), q1])
    normalized_loads = (np.array(loads) - min_load) / (max_load - min_load)
    normalized_q1 = (q1 - min_load) / (max_load - min_load)
    
    # --Apply fuzzy clustering to the normalized loads
    kmeans = KMeans(n_clusters=k, random_state=0)
    fuzzy_labels = kmeans.fit_transform(normalized_loads.reshape(-1, 1))
    
    # --Find the cluster to which the node load belongs
    q1_cluster = np.argmin(np.abs(normalized_q1 - kmeans.cluster_centers_.flatten()))
    
    # --Calculate the overheating similarity based on the fuzzy membership equation
    theta = min(fuzzy_labels[q1_cluster][0], fuzzy_labels[q1_cluster][1])
    phi = max(fuzzy_labels[q1_cluster][1], fuzzy_labels[q1_cluster][2])
    print(theta)
    print(phi)
    overheating_similarity = (q1 - theta) / (phi - theta) if theta <= q1 <= phi else 0 if q1 < theta else 1
    print(overheating_similarity)
    return str(overheating_similarity)

def calculate_overheating_similarity_2(q1,other_node_loads):
    
    if q1 < theta:
        B_q1 = 0
    elif q1 >= phi:
        B_q1 = 1
    else:
        num = q1 - theta
        denom = phi - theta
        B_q1 = num / denom
    return str(B_q1)



def send_file_to_peer(file_path, other_node_loads, q1, theta=0.6, phi=0.9):

    # Calculate the average load of other nodes
    avg_load = sum(other_node_loads) / len(other_node_loads)
    
    # Calculate the proximity to overload based on the difference between q1 and the average load of other nodes
    proximity = abs(q1 - avg_load)
    
    # Check if overheating similarity is within the proximity threshold
    if q1 > theta and q1 < phi and q1 >= avg_load - proximity:
    
        # Select a peer node with less overheating similarity and high degree of links
        selected_peer = None
        max_links = 0
        for i, load in enumerate(other_node_loads):
            # Calculate the proximity to overload of the peer node
            peer_proximity = abs(load - avg_load)
            # Check if the peer node is suitable for replication
            if load < phi and load < q1 and load < avg_load - peer_proximity:
                # Check if the peer node has more links than the current selected node
                links = random.randint(0, 10) # randomly generate number of links
                if links > max_links:
                    selected_peer = i
                    max_links = links
        
        # Send the local file to the selected peer node
        if selected_peer is not None:
            url = f'http://node{selected_peer}/file'
            with open(file_path, 'rb') as f:
                response = requests.post(url, files={'file': f})
            if response.status_code == 200:
                print('File sent successfully')
            else:
                print(f'Failed to send file: {response.status_code}')
        else:
            print('No suitable peer node found for replication')
    else:
        print('Node is not suitable for replication')
    

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug =True,port=5002)




