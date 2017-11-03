import numpy as np
import snap
from collections import defaultdict
import cPickle as pk

data_savefile = 'sampled_brightkite.npy'
socialGraphFilename = 'Brightkite_edges.txt'
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
	tau = {(v,u):tau[(v,u)][0] for (v,u) in tau}
	return Au, Av2u, Avnu, tau,	credit


dicts = learning_phase_1(G, data)
names = ['au.p', 'av2u.p', 'avnu.p', 'tau.p', 'credit.p']
for d, n in zip(dicts, names):
	f = open(n, 'w')
	pickle.dump(d, f)
	f.close()

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
		user = row[user_id_idx]
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