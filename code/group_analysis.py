import numpy as np
import snap
from datetime import datetime, date
from collections import defaultdict
import matplotlib.pyplot as plt

data_savefile = '../data/train_sampled_brightkite.npy'
socialGraphFilename = '../data/Brightkite_edges.txt'
user_id_idx = 0
timestamp_idx = 1
location_id_idx = 2

# Data ordered by location_id, then by time
data = np.load(data_savefile)
Graph = snap.LoadEdgeList(snap.PUNGraph, socialGraphFilename)

group = []
groups = []
previous_location_id = 0
previous_timestamp = date(2000, 1, 1)
for row in data:
	user_id = row[user_id_idx]
	timestamp = row[timestamp_idx].date()
	location_id = row[location_id_idx]
	if (timestamp - previous_timestamp).days > 0 or location_id != previous_location_id:
		if len(group) > 1:
			groups.append(group)
		group = []
	previous_location_id = location_id
	previous_timestamp = timestamp
	if user_id not in group:
		group.append(user_id)

print len(groups)
group_size = defaultdict(int)
for counter, group in enumerate(groups):
	print "Processing: {}/{}".format(counter, len(groups))
	NIdV = snap.TIntV()
	for individual in group:
		NIdV.Add(int(individual))
	SubGraph = snap.GetSubGraph(Graph, NIdV)
	Components = snap.TCnComV()
	snap.GetWccs(SubGraph, Components)
	print "Group Size: {}, NCC: {}".format(len(group), len(Components))
	for CnCom in Components:
		if CnCom.Len() > 1:
			group_size[CnCom.Len()] += 1
			print "Group Found!"

lists = sorted(group_size.items())
print lists
x,y = zip(*lists)
plt.plot(x,y)
# plt.show()



