import csv
import datetime
import os
import random
import threading
import time
import json
from .location import get_location
import pika


class RequestGenerator(threading.Thread):
    def __init__(self, num_files):
        self.connection = None
        self.num_files = num_files
        self.access_pattern = []
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        try:
            super().__init__()
        except Exception as e:
            print("Error while initializing request generator")

    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        print("Request Generator has started and connected to message queue...")
        # first_epoch = None
        # second_epoch = None
        # with open("requests/pattern.csv", newline="") as csvfile:
        #     reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        #     next(reader)
        #     for row in reader:
        #         if first_epoch is None:
        #             first_epoch = datetime.datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M:%S.%f")
        #             continue
        #         # timestamp = 2023-04-01 23:00:34.636319
        #         if second_epoch is None:
        #             second_epoch = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
        #         self.access_pattern.append(int(row[1]))
        #
        # for i in self.access_pattern:
        #     for f in range(i):
        #         file_number = random.randint(1, self.num_files)
        #         request_body = {
        #             "file_id": file_number,
        #             "origin": get_location(),
        #             "timestamp": str(datetime.datetime.now())
        #         }
        #         request = json.dumps(request_body).encode()
        #         self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        #         channel = self.connection.channel()
        #         channel.basic_publish(exchange="",
        #                               routing_key="job_queue",
        #                               body=request)
        #     time.sleep(0.01)
        # print("Done with sending requests")

        with open("requests/requests_transformed.csv", "r") as requests:
            reader = csv.DictReader(requests)
            prev_delta = 0
            count = 0
            for row in reader:
                try:
                    dest_ip = row["dest_ip"]
                    lat = float(row["lat"])
                    long = float(row["lon"])
                    curr_delta = float(row["timestamp_delta"])
                    request_body = {
                        "file_id": (int(dest_ip[-1]) % self.num_files) + 1,
                        "origin": (lat, long),
                        "timestamp": str(datetime.datetime.now())
                    }
                    # print(f"count={count} timestamp={request_body['timestamp']}")
                    request = json.dumps(request_body).encode()
                    self.channel.basic_publish(exchange="", routing_key="job_queue", body=request)
                    time.sleep((curr_delta - prev_delta) / 100)
                    prev_delta = curr_delta
                    count += 1

                except Exception as e:
                    continue

        print("Done with sending requests")
