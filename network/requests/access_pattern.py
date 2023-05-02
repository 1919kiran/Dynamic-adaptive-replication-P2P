import sharedqueue
import random
from datetime import datetime, timedelta
from collections import Counter
import numpy as np
import pandas as pd
import yaml


def generate_timestamps(start, end, distribution_size, max_peaks, min_sample_size, max_sample_size):
    # Converting to timestamp
    start = int(start.timestamp())
    end = int(end.timestamp())

    d = distribution_size
    peaks = 0
    samples = []
    while max_peaks != 0 and d > 0:
        if d < min_sample_size or max_peaks == 1:
            sample_size = d
        else:
            sample_size = random.randint(min_sample_size, max_sample_size)
        d -= sample_size
        max_peaks -= 1
        peaks += 1
        sigma = random.uniform(min_sample_size, max_sample_size)
        loc = random.uniform(start, end)
        # print('loc = ', loc, ' sample size = ', sample_size)
        sample = np.random.gumbel(loc=loc, scale=sigma, size=sample_size)
        # print('sample = ', len(sample))
        samples = samples + sample.tolist()

    return samples


def generate_timestamps_random(start, end, distribution_size, max_peaks, min_sample_size, max_sample_size):
    d = distribution_size
    samples = []

    while d != 0:
        t = random.uniform(start, end)
        samples.append(t)
        d -= 1

    return samples


class FileAccessData:
    total_requests = 0
    request_timestamps = None

    def __init__(self):
        with open("../config.yml", "r") as file:
            data = yaml.full_load(file)
        self.config = data.get("file_data")
        self.request_timestamps = queue.SharedQueue(self.config.get("qsize"))

    def add_requests(self, timestamps):
        for timestamp in timestamps:
            if self.request_timestamps.qsize() >= self.request_timestamps.maxsize:
                print("Queue limit exceeded. Remaining requests are discarded")
                break
            self.request_timestamps.put(timestamp)
            # print(type(timestamp))
        self.total_requests = self.request_timestamps.qsize()

    def group_timestamps(self):
        datetimes = sorted(list(self.request_timestamps.queue), reverse=True)

        df = pd.DataFrame({"freq": datetimes})

        # Group the datetimes into hourly intervals
        df["interval"] = df["freq"].dt.floor("H")

        # Get the frequency counts for each hour
        grouped_df = df.groupby("interval").count()

        return list(grouped_df.itertuples(index=True, name=None))


class AccessPatternGenerator:
    def __init__(self):
        c = dict()
        with open("../config.yml", "r") as file:
            c = yaml.full_load(file)
        self.config = c.get("access_pattern")

    def generate_access_pattern(self):
        start = datetime.now() - timedelta(days=self.config.get("range"))
        end = datetime.now()
        timestamps = generate_timestamps_random(start=start,
                                                end=end,
                                                distribution_size=self.config.get("distribution_size"),
                                                max_peaks=self.config.get("max_peaks"),
                                                min_sample_size=self.config.get("min_sample_size"),
                                                max_sample_size=self.config.get("max_sample_size"))

        return timestamps
