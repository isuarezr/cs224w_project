from datetime import datetime
import numpy as np
import re
from collections import defaultdict
import matplotlib.pyplot as plt

user_id_idx = 0
timestamp_idx = 1
location_id_idx = 2

filename = "Brightkite_totalCheckins.txt"
# filename = 'small_checkins.txt'
format_str = '%Y-%m-%dT%H:%M:%SZ'
data_savefile = 'sampled_brightkite.npy'
# data_savefile = 'small.npy'

def convert_timestamp(data):
	###timestamp format is YYYY-MM-DD<T>HH:MM:SS<Z>
	for i in xrange(len(data)):
		data[i][timestamp_idx] = datetime.strptime(data[i][timestamp_idx], format_str)

data = np.loadtxt(filename, dtype='str', usecols=[0,1,4], delimiter='\t')
print "Loaded data"
# indices = np.random.randint(0, data.shape[0], data.shape[0]/100)
# data = data[indices]
# data = np.load(data_savefile)

min_unique_visits = 5
loc_to_visits = defaultdict(set)
for row in data:
	loc_to_visits[row[location_id_idx]].add(row[user_id_idx])
remove_locs = set([loc for loc in loc_to_visits if len(loc_to_visits[loc]) < min_unique_visits])
data = [row for row in data if row[location_id_idx] not in remove_locs]
print "removed low frequency locs"
all_zeros = re.compile('0+')
data = [list(row) for row in data if not all_zeros.match(row[location_id_idx])]
convert_timestamp(data)

data = sorted(data, key=lambda row: (row[location_id_idx], row[timestamp_idx]))

# to_plot = sorted([(loc, len(loc_to_visits[loc])) for loc in loc_to_visits], key=lambda x: x[1])
# x, y = zip(*to_plot)
# x = range(len(x))

# plt.plot(x, y)
# plt.show()

test_prop = 0.2
k = int(test_prop*len(data))

train_data = data[:-k]
test_data = data[-k:]

loc_to_visits = defaultdict(set)
for row in data:
	loc_to_visits[row[location_id_idx]].add(row[user_id_idx])

np.save('train_'+data_savefile, np.array(train_data))
np.save('test_'+data_savefile, np.array(test_data))

