import queue
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


def generate_timestamps(start, end, distribution_size, max_peaks, min_sample_size, max_sample_size):
    # Converting to timestamp
    start = start.timestamp()
    end = end.timestamp()

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
        # print(sample.tolist())
        samples = samples + sample.tolist()

    return samples


class FileAccessData:
    total_requests = 0
    request_timestamps = None

    def __init__(self):
        self.request_timestamps = queue.Queue(maxsize=1024)

    def add_request(self, timestamp):
        if self.request_timestamps.qsize() >= self.request_timestamps.maxsize:
            print('limit reached')
            return -1
        self.request_timestamps.put(timestamp)
        self.total_requests = self.request_timestamps.qsize()
        return 0


class AccessPatternGenerator:
    def __init__(self):
        c = dict()
        with open("config.yml", "r") as file:
            c = yaml.full_load(file)
        self.config = c
        # print(self.config)

    def generate_access_pattern(self):
        start = datetime.now() - timedelta(days=1)
        end = datetime.now()
        t = generate_timestamps(start=start,
                                end=end,
                                distribution_size=self.config.get("distribution_size"),
                                max_peaks=self.config.get("max_peaks"),
                                min_sample_size=self.config.get("min_sample_size"),
                                max_sample_size=self.config.get("max_sample_size"))

        f = [1 for x in range(len(t))]
        data = {"timestamps": t, "freq": f}
        # Create DataFrame
        df = pd.DataFrame(data)
        df["timestamps"] = pd.to_datetime(df["timestamps"], unit='s')
        df = df.resample(self.config.get("sampling_interval"), on='timestamps').sum()
        df.sort_values(by=["timestamps"], inplace=True, ascending=False)
        plt.plot(df)
        plt.show()

        return list(df.to_records())
