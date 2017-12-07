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
	random_set = set()
	Rnd = snap.TRnd(42)
	Rnd.Randomize()
	for i in range(k):
		random_set.add(G.GetRndNId(Rnd))
	return random_set


slice_name = '../data/sliced_graph.txt'
weights_name = '../saved_dictionaries/sliced-weights.p'

if os.path.isfile(slice_name):
	G_prime = snap.LoadEdgeList(snap.PUNGraph, slice_name)
	f = open(weights_name, 'r')
	weights = pk.load(f)
	f.close()
else:
	G = snap.LoadEdgeList(snap.PUNGraph, '../data/Brightkite_edges.txt')
	f = open('../saved_dictionaries/weights-jaccard.p', 'r')
	weights = pk.load(f)
	f.close()
	checkin_data_filename = '../data/Brightkite_totalCheckins.txt'
	query_location = (39.05, -94.59)
	max_distance = 40
	G_prime, weights_prime = get_graph_slice(G, weights, checkin_data_filename, query_location, max_distance)
	snap.SaveEdgeList(G_prime, slice_name)
	f = open(weights_name, 'w')
	pk.dump(weights_prime, f)
	f.close()

def compare_methods(G, weights, max_k):
	num_trials = 100

	degree_list = [0]
	cluster_list = [0]
	central_list = [0]
	random_list = [0]
	greedy_list = [0]


	degree_m = getHighestDegreeInfluenceSet(G_prime, max_k)
	cluster_m = getHighestClusteringCoefficientInfleunceSet(G_prime, max_k)
	central_m = getHighestBetweenessCentralityInfluenceSet(G_prime, max_k)
	greedy_m = hill_climb(G, weights, max_k)

	for k in range(1, max_k+1):
		degree = set(degree_m[:k])
		cluster = set(cluster_m[:k])
		central = set(central_m[:k])
		greedy = set(greedy_m[:k])
		random = getRandomInfluenceSet(G_prime, k)

		degree_list.append(computeAverageInfluenceSetSize(G, weights, degree, num_trials))
		cluster_list.append(computeAverageInfluenceSetSize(G, weights, cluster, num_trials))
		central_list.append(computeAverageInfluenceSetSize(G, weights, central, num_trials))
		random_list.append(computeAverageInfluenceSetSize(G, weights, random, num_trials))
		greedy_list.append(computeAverageInfluenceSetSize(G, weights, greedy, num_trials))

	degree_h, = plt.plot(degree_list, label='High Degree')
	cluster_h, = plt.plot(cluster_list, label='High Clust. Coef.')
	central_h, = plt.plot(central_list, label='High Betw. Cent.')
	random_h, = plt.plot(random_list, label='Random')
	greedy_h, = plt.plot(greedy_list, label='Greedy Alg.')

	plt.xlabel("Target Set Size")
	plt.ylabel("Active Set Size")

	plt.legend(handles=[degree_h, cluster_h, central_h, random_h, greedy_h])
	plt.savefig("methods_comparison.png")
	plt.show()

compare_methods(G_prime, weights_prime, 30)
