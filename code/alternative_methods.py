'''
For graph, for given k, return k best nodes based on heuristics 
'''

import snap
from heapq import nlargest
import os
from location_filtering import *
import cPickle as pk
import matplotlib.pyplot as plt
from influence_set import *
from collections import defaultdict

def getHighestDegreeInfluenceSet(G, k):
	degree_node_pairs = [(node.GetDeg(), node.GetId()) for node in G.Nodes()]
	k_best = sorted(nlargest(k, degree_node_pairs), reverse=True)
	return [pair[1] for pair in k_best]

def getHighestBetweenessCentralityInfluenceSet(G, k):
	Nodes = snap.TIntFltH()
	Edges = snap.TIntPrFltH()
	snap.GetBetweennessCentr(G, Nodes, Edges, 0.5)
	centrality_node_pairs = [(Nodes[node], node) for node in Nodes]
	k_best = sorted(nlargest(k, centrality_node_pairs), reverse=True)
	return [pair[1] for pair in k_best]

def getHighestClusteringCoefficientInfleunceSet(G, k):
	NIdCCfH = snap.TIntFltH()
	snap.GetNodeClustCf(G, NIdCCfH)
	centrality_node_pairs = [(NIdCCfH[node], node) for node in NIdCCfH if G.GetNI(node).GetDeg() >= 5]
	k_best = sorted(nlargest(k, centrality_node_pairs), reverse=True)
	return [pair[1] for pair in k_best]

def getRandomInfluenceSet(G, k):
	random_set = []
	Rnd = snap.TRnd(42)
	Rnd.Randomize()
	for i in range(k):
		random_set.append(G.GetRndNId(Rnd))
	return random_set

slice_name = '../data/sliced_graph.txt'
weights_name = '../saved_dictionaries/sliced-weights.p'
weights_blind_name = '../saved_dictionaries/sliced-blind-weights.p'

oakland = (37.8, -122.27)
new_york = (40.71, -74.01)

# if os.path.isfile(slice_name):
# 	G_prime = snap.LoadEdgeList(snap.PUNGraph, slice_name)
# 	f = open(weights_name, 'r')
# 	weights_prime = pk.load(f)
# 	f.close()
# 	f = open(weights_blind_name, 'r')
# 	weights_blind_prime = pk.load(f)
# 	f.close()
# else:
# 	G = snap.LoadEdgeList(snap.PUNGraph, '../data/Brightkite_edges.txt')
# 	f = open('../saved_dictionaries/weights-bernoulli.p', 'r')
# 	weights = pk.load(f)
# 	f.close()
# 	f = open('../saved_dictionaries/weights-blind-bernoulli.p', 'r')
# 	weights_blind = pk.load(f)
# 	f.close()

# 	checkin_data_filename = '../data/Brightkite_totalCheckins.txt'
# 	query_location = new_york
# 	max_distance = 500
# 	G_prime, weights_prime, weights_blind_prime = get_graph_slice(G, weights, weights_blind, checkin_data_filename, query_location, max_distance)
# 	snap.SaveEdgeList(G_prime, slice_name)
# 	G_prime = snap.LoadEdgeList(snap.PUNGraph, slice_name) #easiest way to get rid of 0 degree nodes
# 	f = open(weights_name, 'w')
# 	pk.dump(weights_prime, f)
# 	f.close()
# 	f = open(weights_blind_name, 'w')
# 	pk.dump(weights_blind_prime, f)
# 	f.close()

G = snap.LoadEdgeList(snap.PUNGraph, '../data/Brightkite_edges.txt')
f = open('../saved_dictionaries/weights-bernoulli.p', 'r')
weights = pk.load(f)
f.close()
f = open('../saved_dictionaries/weights-priors-bernoulli.p', 'r')
weights_priors = pk.load(f)
f.close()

checkin_data_filename = '../data/Brightkite_totalCheckins.txt'
user_locations = get_user_locations(checkin_data_filename)
query_location = new_york
max_distance = 500

def compare_prior(G, weights, weights_priors, user_locations, query_location, k):
	distances = [25, 50, 100, 200, 300, 400, 500, 750, 1000]
	# distances = [300, 500]

	greedy_list = []
	greedy_prior_list = []
	for distance in distances:
		query_location = new_york
		nearby_users = slice_users(user_locations, query_location, distance)
		G_prime = slice_graph(G, nearby_users)
		weights_prime = slice_weights(weights, nearby_users)
		weights_priors_prime = slice_weights(weights_priors, nearby_users)
		snap.SaveEdgeList(G_prime, slice_name)
		G_prime = snap.LoadEdgeList(snap.PUNGraph, slice_name) #easiest way to get rid of 0 degree nodes
		
		greedy_m = CELF(G_prime, weights_prime, k)
		greedy_list.append(computeAverageInfluenceSetSize(G_prime, weights_prime, greedy_m, k))

		greedy_prior_m = CELF(G_prime, weights_priors_prime, k)
		greedy_prior_list.append(computeAverageInfluenceSetSize(G_prime, weights_priors_prime, greedy_prior_m, k))

	greedy_h, = plt.plot(distances, greedy_list, label='Greedy Alg.')
	greedy_prior_h, = plt.plot(distances, greedy_prior_list, label='Greedy Alg. with distance considerations')

	plt.xlabel("Distance from Oakland (km)")
	plt.ylabel("Active Set Size with k={}".format(k))

	plt.legend(handles=[greedy_h, greedy_prior_h])
	plt.savefig("location_sensitivity_comparison.png")
	plt.show()

compare_prior(G, weights, weights_priors, user_locations, query_location, k=15)


def compare_methods(G, weights, weights_blind, max_k):
	print "G has {} nodes".format(G.GetNodes())
	num_trials = 1000

	degree_list = [0]
	cluster_list = [0]
	central_list = [0]
	random_list = [0]
	greedy_list = [0]
	blind_greedy_list = [0]

	degree_m = getHighestDegreeInfluenceSet(G, max_k)
	cluster_m = getHighestClusteringCoefficientInfleunceSet(G, max_k)
	central_m = getHighestBetweenessCentralityInfluenceSet(G, max_k)
	random_m = getRandomInfluenceSet(G, max_k)
	# blind_greedy_m = CELF(None, weights_blind, max_k, num_trials)
	greedy_m = CELF(G, weights, max_k, num_trials)
	try:
		# print blind_greedy_m
		print greedy_m
	except:
		pass

	for k in range(1, max_k+1):
		degree = set(degree_m[:k])
		cluster = set(cluster_m[:k])
		central = set(central_m[:k])
		random = set(random_m[:k])
		greedy = set(greedy_m[:k])
		# blind_greedy = set(blind_greedy_m[:k])

		degree_list.append(computeAverageInfluenceSetSize(G, weights, degree, num_trials))
		cluster_list.append(computeAverageInfluenceSetSize(G, weights, cluster, num_trials))
		central_list.append(computeAverageInfluenceSetSize(G, weights, central, num_trials))
		random_list.append(computeAverageInfluenceSetSize(G, weights, random, num_trials))
		greedy_list.append(computeAverageInfluenceSetSize(G, weights, greedy, num_trials))
		# blind_greedy_list.append(computeAverageInfluenceSetSize(G, weights, blind_greedy, num_trials))

	degree_h, = plt.plot(degree_list, label='High Degree')
	cluster_h, = plt.plot(cluster_list, label='High Clust. Coef.')
	central_h, = plt.plot(central_list, label='High Betw. Cent.')
	random_h, = plt.plot(random_list, label='Random')
	greedy_h, = plt.plot(greedy_list, label='Greedy Alg.')
	# blind_greedy_h, = plt.plot(blind_greedy_list, label='Blind Greedy Alg.')

	plt.xlabel("Target Set Size")
	plt.ylabel("Active Set Size")

	# plt.legend(handles=[degree_h, cluster_h, central_h, random_h, greedy_h, blind_greedy_h])
	plt.legend(handles=[degree_h, cluster_h, central_h, random_h, greedy_h])
	plt.savefig("methods_comparison.png")
	plt.show()

# compare_methods(G_prime, weights_prime, weights_blind_prime, 50)
