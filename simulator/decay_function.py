from datetime import datetime
import numpy as np
import yaml
import pytz
from tzlocal import get_localzone

class DecayFunctionCalculator:
    def __init__(self):
        c = dict()
        with open("config.yml", "r") as file:
            c = yaml.full_load(file)
        self.config = c.get("decay_function")

    def compute_decay_factor(self, grouped_timestamps, initial_freq, time_delta):
        access_weight = 0
        decay_rate = self.config.get("decay_rate")
        for access in grouped_timestamps:
            pass
            # print(access[0].to_pydatetime())
            time_delta = (datetime.now() - access[0].to_pydatetime()).total_seconds() / 3600
            # print(time_delta)
            freq = access[1]
            w = freq * abs(1 - decay_rate) ** time_delta
            print("freq = ", freq, " , time_delta = ", time_delta, " , w = ", w)
            access_weight += w
        return access_weight
