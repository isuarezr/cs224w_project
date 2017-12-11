import snap
from location_filtering import *
from sklearn.linear_model import LogisticRegression
from collections import defaultdict
import random
import numpy as np
import cPickle as pk

checkin_data_filename = '../data/Brightkite_totalCheckins.txt'
socialGraphFilename = '../data/Brightkite_edges.txt'

user_to_home = get_user_locations(checkin_data_filename)

user_id_idx = 0
timestamp_idx = 1
latitude_idx = 2
longitude_idx = 3
location_id_idx = 4

data = np.loadtxt(checkin_data_filename, dtype='str', usecols=[0,1,2,3,4], delimiter='\t')
G = snap.LoadEdgeList(snap.PUNGraph, socialGraphFilename)

X = []
y = []

locations_to_counts = defaultdict(int)
locations_to_users = defaultdict(set)
users_to_counts = defaultdict(int)
locations_to_latlng = {}

print "Processing Positive Examples"
for row in data:
	user = int(row[user_id_idx])
	timestamp = row[timestamp_idx]
	try:
		lat = float(row[latitude_idx])
		lng = float(row[longitude_idx])
	except:
		continue
	action = row[location_id_idx]
	active_location = (lat, lng)
	user_location = user_to_home[user]
	distance = float(get_distance_km(active_location, user_location))
	X.append([distance, distance**2, distance**3, distance**4, distance**5])
	y.append(1)
	locations_to_counts[action] += 1
	locations_to_users[action].add(user)
	users_to_counts[user] += 1
	locations_to_latlng[action] = (lat,lng)

locations, counts = zip(*locations_to_counts.items())
locations = list(locations)
counts = list(counts)
n = sum(counts)
probs = [float(count)/n for count in counts]
chosen_indices = np.random.choice(range(len(locations)), len(data)*2, p=probs)
chosen_locations = []
for idx in chosen_indices:
	chosen_locations.append(locations[idx])

users, counts = zip(*users_to_counts.iteritems())
users = list(users)
counts = list(counts)
probs = [float(count)/n for count in counts]
chosen_indices = np.random.choice(range(len(users)), len(data)*2)
chosen_users = []
for idx in chosen_indices:
	chosen_users.append(users[idx])

print "Processing Negative Examples"
for i in range(len(chosen_locations)):
	next_location = chosen_locations[i]
	next_user = chosen_users[i]
	if next_user in locations_to_users[next_location]:
		continue
	if len(X) >= 2*n:
		break
	active_location = locations_to_latlng[next_location]
	user_location = user_to_home[next_user]
	distance = float(get_distance_km(active_location, user_location))
	X.append([distance, distance**2, distance**3, distance**4, distance**5])
	y.append(0)

# c = list(zip(X, y))
# random.shuffle(c)
# X, y = zip(*c)
# training_examples = int(0.7*len(X))
# X_train = X[:training_examples]
# y_train = y[:training_examples]
# X_test = X[training_examples:]
# y_test = y[training_examples:]

logistic = LogisticRegression()
logistic.fit(X,y)
pred = logistic.predict(X)

correct_p = 0

for i in range(len(pred)):
	if pred[i] == y[i]:
		correct_p += 1

accuracy = float(correct_p)/len(pred)
print "Accuracy: {}".format(accuracy)
f = open('../saved_dictionaries/prior.p', 'w')
pk.dump(logistic, f)
f.close()



