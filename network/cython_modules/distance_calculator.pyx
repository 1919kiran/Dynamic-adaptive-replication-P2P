import cython
import math
import numpy as np

@cython.boundscheck(False)
@cython.wraparound(False)
def haversine_distance(double lat1, double lon1, double lat2, double lon2):
    cdef double R = 6371000.0
    cdef double dlat = np.radians(lat2 - lat1)
    cdef double dlon = np.radians(lon2 - lon1)
    cdef double a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    cdef double c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    cdef double distance = R * c
    return distance

@cython.boundscheck(False)
@cython.wraparound(False)
def euclidean_distance(double lat1, double lon1, double lat2, double lon2):
    cdef double x = lat2 - lat1
    cdef double y = lon2 - lon1
    return math.sqrt(x*x + y*y)
