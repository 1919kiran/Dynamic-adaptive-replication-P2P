from network.requests.access_pattern import FileAccessData


def create_file_access_data(access_pattern):
    file_access_data = FileAccessData()


def normalize(lst):
    min_value = min(lst)
    max_value = max(lst)
    range_value = max_value - min_value
    res = []
    for x in lst:
        if range_value == 0:
            res.append(0)
        else:
            res.append((x - min_value) / range_value)
    return res
