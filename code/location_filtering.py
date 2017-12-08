import snap
import numpy as np
import geopy.distance
from collections import defaultdict
import cPickle as pk
import random

#make sure each location is (LATITUDE, LONGITUDE)
def get_distance_km(location_1, location_2):
	return geopy.distance.vincenty(location_1, location_2)

#return longitude, latitude where we think each user lives
def get_user_locations(checkin_data_filename):
	print "Getting user locations"
	data = np.loadtxt(checkin_data_filename, dtype='str', usecols=[0,2,3], delimiter='\t')
	print "Checkins loaded"
	user_to_locations = defaultdict(list)
	for user, latitude, longitude in data:
		user = int(user)
		try:
			latitude = float(latitude)
			longitude = float(longitude)
		except:
			continue
		user_to_locations[user].append((latitude, longitude))
	user_to_home = {}
	num_iters = len(user_to_locations)
	print num_iters
	iters = 0
	for user in user_to_locations:
		user_to_home[user] = compute_user_location(user_to_locations[user])
	return user_to_home

def compute_user_location(locations):
	n = len(locations)
	latitude = sum([locations[i][0] for i in range(n)]) / n
	longitude = sum([locations[i][1] for i in range(n)]) / n
	return (latitude, longitude)

#return a slice of G based on the query location
def get_graph_slice(G, weights, weights_blind, checkin_data_filename, query_location, max_distance):
	user_locations = get_user_locations(checkin_data_filename)
	user_distance_pairs = [(user, get_distance_km(query_location, user_locations[user])) for user in user_locations]
	far_users = [user for user, dist in user_distance_pairs if dist > max_distance]
	V = snap.TIntV()
	for user in far_users:
		V.Add(user)
	G_prime = snap.ConvertGraph(type(G), G)
	old_G_size = G.GetNodes()
	snap.DelNodes(G_prime, V)
	assert G.GetNodes() == old_G_size

	sliced_users = set([node.GetId() for node in G_prime.Nodes()])
	sliced_weights = {}
	for u,v in weights:
		if u in sliced_users and v in sliced_users and weights[(u,v)] > 0:
			sliced_weights[(u,v)] = weights[(u,v)]

	sliced_weights_blind = {}
	for u,v in weights_blind:
			if u in sliced_users and v in sliced_users:
				sliced_weights_blind[(u,v)] = weights_blind[(u,v)]
	###give each user k random friends in this network
	def select_randomly(weights, k=10):
		weights_map = defaultdict(lambda: defaultdict(float))
		for (u,v), w in weights.iteritems():
			weights_map[u][v] = w

		weights_map_filtered = defaultdict(dict)
		for u in weights_map:
			neighbors = weights_map[u].keys()
			random.shuffle(neighbors)
			neighbors = neighbors[:k]
			for v in neighbors:
				weights_map_filtered[u][v] = weights_map[u][v]
		print "After selecting neighbors, {} nodes in weight map".format(len(weights_map_filtered))
		return weights_map_filtered

	sliced_weights_blind = select_randomly(sliced_weights_blind, 5)

	return G_prime, sliced_weights, sliced_weights_blind

# slice_name = '../data/sliced_graph.txt'
# G = snap.LoadEdgeList(snap.PUNGraph, '../data/Brightkite_edges.txt')
# weights_name = '../saved_dictionaries/predicted_weights.p'
# f = open(weights_name, 'r')
# weights = pk.load(f)
# f.close()
# checkin_data_filename = '../data/Brightkite_totalCheckins.txt'
# query_location = (41.67, -72.14)
# max_distance = 500
# G_prime, weights_prime = get_graph_slice(G, weights, checkin_data_filename, query_location, max_distance)
# snap.SaveEdgeList(G_prime, slice_name)
# G_prime = snap.LoadEdgeList(snap.PUNGraph, slice_name) #easiest way to get rid of 0 degree nodes

# weights_slice_name = '../saved_dictionaries/sliced_predicted_weights.p'
# f = open(weights_slice_name, 'w')
# pk.dump(weights_prime, f)
# f.close()