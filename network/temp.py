import time
import datetime
import csv
import random

first_epoch = None
second_epoch = None
access_pattern = []

with open('../input/pattern.csv', newline='') as csvfile:
    # Create a CSV reader object
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(reader)
    for row in reader:
        if first_epoch is None:
            first_epoch = datetime.datetime.strptime(str(row[0]), '%Y-%m-%d %H:%M:%S.%f')
            continue
        # timestamp = 2023-04-01 23:00:34.636319
        if second_epoch is None:
            second_epoch = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
            delta = (second_epoch - first_epoch).total_seconds()
        access_pattern.append(int(row[1]))


num_files = 10
files_access = {i: 0 for i in range(1, num_files+1)}
for t in access_pattern:
    files = ""
    for f in range(t):
        random_file = random.randint(1, num_files)
        files_access[random_file] += 1
        files = files + "file {} ".format(random_file)
    print("making requests for files: ", files)
    time.sleep(delta/10)

print(files_access)
