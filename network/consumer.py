import pika
import json
import signal
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare the queue you want to consume from
channel.queue_declare(queue='metrics_queue', durable=True)

bandwidth = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: []
}
latency = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: []
}
timestamps = []

start = datetime.now()


# Define the callback function that will be called when a message is received
def callback(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))
    node_id = data["node_id"]
    bw = data["bandwidth"]
    lat = data["avg_latency"]
    bandwidth[node_id].append(bw)
    latency[node_id].append(lat)
    timestamps.append(datetime.now())


# Start consuming messages
channel.basic_consume(queue='metrics_queue', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit, press Ctrl+C')


def signal_handler(sig, frame):
    print("Ctrl+C detected. Exiting gracefully...")
    # t = pd.date_range(start=start, end=datetime.now()., periods=len(bandwidth[1]))
    # plt.plot(t, bandwidth[1])
    # plt.xlabel('Timestamp')
    # plt.ylabel('Bandwidth')
    # plt.title('Bandwidth over Time')
    # plt.xticks(rotation=45)
    # plt.show()
    with open("../data-extraction/data-worstcase.txt", "w") as file:
        file.write(json.dumps({
            "bandwidth": bandwidth,
            "latency": latency
        }))

    exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Start consuming messages indefinitely
channel.start_consuming()
