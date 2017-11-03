import numpy as np
import snap
from collections import defaultdict

data_savefile = 'sampled_brightkite.npy'
socialGraphFilename = 'Brightkite_edges.txt'
user_id_idx = 0
timestamp_idx = 1
location_id_idx = 2

data = np.load(data_savefile)
G = snap.LoadEdgeList(snap.PUNGraph, socialGraphFilename)

Au = defaultdict(int)
Av2u = defaultdict(int)
Avnu = defaultdict(int)
tau = defaultdict(lambda : (0., 0))
credit = {}

curr_action = data[0][location_id_idx]
current_table = set()
i = 0
n = len(data)
for row in data:
	i += 1
	if i % 10000 == 0:
		print "Finished with iter {} of {}".format(i, n)
		print "tau has {} entries".format(len(tau.keys()))
	user = row[user_id_idx]
	timestamp = row[timestamp_idx]
	action = row[location_id_idx]
	if action != curr_action:
		# Move to next action
		curr_action = action
		current_table = set()
	Au[user] += 1
	parents = set()
	for previous_row in current_table:
		previous_user, previous_action, previous_timestamp = previous_row
		if G.IsEdge(int(user), int(previous_user)):
			if (timestamp - previous_timestamp).days > 0:
				Av2u[(previous_user, user)] += 1
				parents.add(previous_user)
				# Instead of average, we were lazy and just did max.
				val, count = tau[(previous_user, user)]
				tau[(previous_user, user)] = (float((val * count) + (timestamp - previous_timestamp).days) / (count + 1), count + 1)
			Avnu[(previous_user,user)] += 1
	for p in parents:
		credit[(p, user, curr_action)] = 1.0/len(parents)
	current_table.add((user, action, timestamp))

