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
CUTOFF_DATE = datetime(2010, 6, 1)

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

N = defaultdict(int)
D = defaultdict(int)

for count, location in enumerate(locations):
	print "Processing location: {}/{}".format(count, len(locations))
	users_in_loc = location_user[location]
	users_in_loc = list(users_in_loc)
	for user in users_in_loc:
		D[user] += 1
	for i in range(len(users_in_loc)):
		for j in range(i+1, len(users_in_loc)):
			N[(users_in_loc[i], users_in_loc[j])] += 1

users = list(users)
for i in range(len(users)):
	print "Processing user: {}/{}".format(i+1, len(users))
	u1 = users[i]
	for j in range(i+1, len(users)):
		u2 = users[j]
		weights[(u1, u2)] = float(N[(u1, u2)] + N[(u2, u1)]) / (D[u1] + D[u2]) 
		weights[(u2, u1)] = weights[(u1, u2)]




# month_user_location = defaultdict(lambda : defaultdict(set))

# for row in data:
# 	user = int(row[user_id_idx])
# 	timestamp = row[timestamp_idx]
# 	action = row[location_id_idx]
# 	month = (timestamp.year, timestamp.month)
# 	month_user_location[month][user].add(action)
# 	users.add(user)
# 	months.add(month)

# weights = {}

# users = list(users)

# for i in range(len(users)):
# 	print "Processing user {}/{}".format(i+1, len(users))
# 	for j in range(i+1, len(users)):
# 		user1 = users[i]
# 		user2 = users[j]
# 		if user1 != user2:
# 			user_iou = []
# 			for month in months:
# 				locations1 = month_user_location[month][user1]
# 				locations2 = month_user_location[month][user2]
# 				union_locations = len(locations1.union(locations2))
# 				if union_locations != 0:
# 					iou = len(locations1.intersection(locations2)) * 1.0 / union_locations
# 				else:
# 					iou = 0
# 				user_iou.append(iou)
# 			weights[(user1, user2)] = sorted(user_iou)[len(user_iou)/2]

f = open('../saved_dictionaries/predicted_weights.p', 'w')
pk.dump(weights, f)
f.close()


