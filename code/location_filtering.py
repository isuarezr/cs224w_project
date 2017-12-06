import snap
import numpy as np
import geopy.distance
from collections import defaultdict

#make sure each location is (LATITUDE, LONGITUDE)
def get_distance_km(location_1, location_2):
	return geopy.distance.vincenty(location_1, location_2)

#return longitude, latitude where we think each user lives
def get_user_locations(checkin_data_filename):
	data = np.loadtxt(filename, dtype='str', usecols=[0,2,3], delimiter='\t')
	user_to_locations = defaultdict(list)
	for user, latitude, longitude in data:
		user = int(user)
		latitude = float(latitude)
		longitude = float(longitude)
		user_to_locations.append((latitude, longitude))
	user_to_home = {}
	for user in user_to_locations:
		user_to_home[user] = compute_user_location(user_locations[user])
	return user_to_home

def compute_user_location(user_locations):
	def average_location(locations):
		n = len(locations)
		latitude = sum[locations[i][0] for i in range(n)] / n
		longitude = sum[locations[i][1] for i in range(n)] / n
		return (latitude, longitude)

	n = len(user_locations)
	for i in xrange(n/2):
		centroid = average_location(user_locations)
		furthest_idx = max([(get_distance_km(centroid, user_locations[i]), i) for i n range(len(user_locations))])[1]
		user_locations.pop(furthest_idx)
	return average_location(user_locations)

#return a slice of G based on the query location
def get_graph_slice(G, checkin_data_filename, query_location, max_distance):
	user_locations = get_user_locations(checkin_data)
	user_distance_pairs = [(user, get_distance_km(query_location, user_locations[user])) for user in user_locations]
	far_users = [user for user, dist in user_distance_pairs if dist > max_distance]
	V = snap.TIntV()
	for user in far_users:
		V.add(user)
	G_prime = snap.ConvertGraph(type(G), G)
	old_G_size = G.GetNodes()
	snap.DelNodes(G_prime, V)
	assert G.GetNodes() == old_G_size
	return G_prime

