import numpy as np
from collections import defaultdict
import numpy as np
import cPickle as pk
from datetime import datetime

data_savefile = '../data/train_sampled_brightkite.npy'
data = np.load(data_savefile)

user_id_idx = 0
timestamp_idx = 1
location_id_idx = 2
users = set()
months = set()
locations = set()

location_user = defaultdict(set)
CUTOFF_DATE = datetime(2010, 5, 1)

for row in data:
	user = int(row[user_id_idx])
	timestamp = row[timestamp_idx]
	if timestamp < CUTOFF_DATE:
		continue
	action = row[location_id_idx]
	location_user[action].add(user)
	users.add(user)
	locations.add(action)

weights = {}

N = defaultdict(float)
D = defaultdict(float)

for count, location in enumerate(locations):
	# print "Processing location: {}/{}".format(count+1, len(locations))
	users_in_loc = location_user[location]
	users_in_loc = list(users_in_loc)
	n = len(users_in_loc)
	for user in users_in_loc:
		D[user] += 1
	for i in range(len(users_in_loc)):
		for j in range(i+1, len(users_in_loc)):
			N[(users_in_loc[i], users_in_loc[j])] += 1

users = list(users)
for i in range(len(users)):
	# print "Processing user: {}/{}".format(i+1, len(users))
	u1 = users[i]
	for j in range(i+1, len(users)):
		u2 = users[j]
		weights[(u1, u2)] = 2*float(N[(u1, u2)] + N[(u2, u1)]) / (D[u1] + D[u2])
		weights[(u2, u1)] = weights[(u1, u2)]

f = open('../saved_dictionaries/predicted_weights.p', 'w')
pk.dump(weights, f)
f.close()


