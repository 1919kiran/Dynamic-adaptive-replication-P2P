import csv
import datetime
import random
import threading
import time
import json
from location import get_location
import pika


class RequestGenerator(threading.Thread):
    def __init__(self, num_files):
        self.connection = None
        self.num_files = num_files
        self.access_pattern = []
        try:
            super().__init__()
        except Exception as e:
            print("Error while initializing request generator")

    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        print("Request Generator has started and connected to message queue...")
        first_epoch = None
        second_epoch = None
        with open("../input/pattern.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            next(reader)
            for row in reader:
                if first_epoch is None:
                    first_epoch = datetime.datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M:%S.%f")
                    continue
                # timestamp = 2023-04-01 23:00:34.636319
                if second_epoch is None:
                    second_epoch = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
                self.access_pattern.append(int(row[1]))

        for i in self.access_pattern:
            for f in range(i):
                file_number = random.randint(1, self.num_files)
                request_body = {
                    "file_id": file_number,
                    "origin": get_location()
                }
                request = json.dumps(request_body).encode()
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
                channel = self.connection.channel()
                channel.basic_publish(exchange="",
                                      routing_key="job_queue",
                                      body=request)
            time.sleep(0.01)
        print("Done with sending requests")
