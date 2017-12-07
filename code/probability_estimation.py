import numpy as np
import snap
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import cPickle as pk

data_savefile = '../data/train_sampled_brightkite.npy'
socialGraphFilename = '../data/Brightkite_edges.txt'
# data_savefile = 'train_small.npy'
# socialGraphFilename = 'small_edges.txt'
user_id_idx = 0
timestamp_idx = 1
location_id_idx = 2

data = np.load(data_savefile)
G = snap.LoadEdgeList(snap.PUNGraph, socialGraphFilename)

### LEARNING PHASE 1

def learning_phase_1(G, data):
	Au = defaultdict(int)
	Av2u = defaultdict(int)
	Avnu = defaultdict(int)
	tau = defaultdict(lambda : (0., 0))
	credit = {}

	curr_action = data[0][location_id_idx]
	current_table = set()
	current_table_users = set()
	i = 0
	n = len(data)
	for row in data:
		i += 1
		if i % 10000 == 0:
			print "Finished with iter {} of {}".format(i, n)
			print "tau has {} entries".format(len(tau.keys()))
		user = int(row[user_id_idx])
		timestamp = row[timestamp_idx]
		action = row[location_id_idx]
		if action != curr_action:
			# Move to next action
			curr_action = action
			current_table_users = set()
			current_table = set()
		if user in current_table_users:
			continue
		Au[user] += 1
		parents = set()
		for previous_row in current_table:
			previous_user, previous_timestamp = previous_row
			if G.IsEdge(int(user), int(previous_user)):
				Av2u[(previous_user, user)] += 1
				parents.add(previous_user)
				# Instead of average, we were lazy and just did max.
				val, count = tau[(previous_user, user)]
				tau[(previous_user, user)] = (float((val * count) + (timestamp - previous_timestamp).days) / (count + 1), count + 1)
				Avnu[(previous_user,user)] += 1
		for p in parents:
			credit[(p, user, curr_action)] = 1.0/len(parents)
		if user not in current_table_users:
			current_table_users.add(user)
			current_table.add((user, timestamp))
	tau = {(v,u):tau[(v,u)][0] for (v,u) in tau}
	return Au, Av2u, Avnu, tau,	credit

def learning_phase_2(G, data, tau):
	### LEARNING PHASE 2
	Av2u_tau = defaultdict(int)
	credit_tau = {}
	infl_u = defaultdict(set)
	i = 0
	n = len(data)
	curr_action = data[0][location_id_idx]
	current_table = set()
	for row in data:
		i += 1
		if i % 10000 == 0:
			print "Finished with iter {} of {}".format(i, n)
		user = int(row[user_id_idx])
		timestamp = row[timestamp_idx]
		action = row[location_id_idx]
		if action != curr_action:
			# Move to next action
			curr_action = action
			current_table = set()
		parents = set()
		for previous_row in current_table:
			previous_user, previous_action, previous_timestamp = previous_row
			if G.IsEdge(int(user), int(previous_user)):
				if 0 < (timestamp - previous_timestamp).days < tau[(previous_user, user)]:
					Av2u_tau[(previous_user, user)] += 1
					parents.add(previous_user)
					# Instead of average, we were lazy and just did max.
		for p in parents:
			credit_tau[(p, user, curr_action)] = 1.0/len(parents)
		if parents:
			infl_u[user].add(action)
		current_table.add((user, action, timestamp))
	infl_u = {user:len(infl_u[user]) for user in infl_u}
	return Av2u_tau, credit_tau, infl_u

dicts = learning_phase_1(G, data)
print "Finished learning phase 1"
names = ['au.p', 'av2u.p', 'avnu.p', 'tau.p', 'credit.p']
for d, n in zip(dicts, names):
	f = open(n, 'w')
	pk.dump(d, f)
	f.close()

# dicts = learning_phase_2(G, data, dicts[3])
# print "Finished learning phase 2"
# names = ['av2u_tau.p', 'credit_tau.p', 'infl_u.p']
# for d, n in zip(dicts, names):
# 	f = open(n, 'w')
# 	pk.dump(d, f)
# 	f.close()