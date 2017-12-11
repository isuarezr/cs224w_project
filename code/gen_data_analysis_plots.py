import numpy as np
import snap
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import cPickle as pk
import re
import os

def plot_degree_distribution(G, name):
	degrees = [node.GetDeg() for node in G.Nodes()]
	freqs = Counter(degrees)
	x = sorted(freqs.keys())
	y = [freqs[val] for val in x]
	cumulative = np.cumsum(y)
	cumulative = cumulative / float(np.sum(y))
	plt.title("Cumulative degree distribution for {} social network".format(name))
	plt.xlabel("Number of friends")
	plt.ylabel("Proportion of nodes")
	plt.semilogx(x,cumulative)
	plt.savefig("{}_deg_dist.png".format(name))
	plt.show()

def plot_visits_per_loc(data, name):
	loc_to_visits = defaultdict(set)
	for row in data:
		loc_to_visits[row[location_id_idx]].add(row[user_id_idx])
	visits = map(len, loc_to_visits.values())
	freqs = Counter(visits)
	x = sorted(freqs.keys())
	y = [freqs[val] for val in x]
	cumulative = np.cumsum(y)
	cumulative = cumulative / float(np.sum(y))
	plt.title("Cumulative distribution of unique user visits for {} locations".format(name))
	plt.xlabel("Number of unique user visits")
	plt.ylabel("Proportion of locations")
	plt.semilogx(x,cumulative)
	plt.savefig("{}_user_visits_to_loc.png".format(name))
	plt.show()

def plot_visits_per_user(data, name):
	user_to_visits = defaultdict(set)
	for row in data:
		user_to_visits[row[user_id_idx]].add(row[location_id_idx])
	visits = map(len, user_to_visits.values())
	freqs = Counter(visits)
	x = sorted(freqs.keys())
	y = [freqs[val] for val in x]
	cumulative = np.cumsum(y)
	cumulative = cumulative / float(np.sum(y))
	plt.title("Cumulative distribution of unique location visits for {} users".format(name))
	plt.xlabel("Number of unique locations visited")
	plt.ylabel("Proportion of users")
	plt.semilogx(x,cumulative)
	plt.savefig("{}_location_visits_for_users.png".format(name))
	plt.show()

name = 'Brightkite'
socialGraphFilename = '../data/Brightkite_edges.txt'
checkinFilename = "../data/Brightkite_totalCheckins.txt"
usecols = [0,1,4]
user_id_idx = 0
timestamp_idx = 1
location_id_idx = 2

savefile = '../data/saved_{}.npy'.format(name)
if os.path.isfile(savefile):
	data = np.load(savefile)
else:
	data = np.loadtxt(checkinFilename, dtype='str', usecols=usecols, delimiter='\t')
	all_zeros = re.compile('0+')
	data = [list(row) for row in data if not all_zeros.match(row[location_id_idx])]
	np.save(savefile, data)

G = snap.LoadEdgeList(snap.PUNGraph, socialGraphFilename)
# plot_degree_distribution(G, name)
# plot_visits_per_loc(data, name)
plot_visits_per_user(data, name)
