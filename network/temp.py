from cython_modules import distance_calculator

import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the haversine distance between two points on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000  # Radius of earth in kilometers. Use 3956 for miles
    return c * r



dist = distance_calculator.haversine_distance(6.607662345511912, -113.06342330255615, -53.754444543459236, 68.6823710697071)

dist2 = haversine_distance(6.607662345511912, -113.06342330255615, -53.754444543459236, 68.6823710697071)

latency = distance_calculator.round_trip_time(6.607662345511912, -113.06342330255615, -53.754444543459236, 68.6823710697071)

print(latency)