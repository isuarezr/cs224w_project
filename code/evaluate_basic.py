import numpy as np
import snap
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import cPickle as pk

def bernoulli(G, av2u_dict, au_dict, av2u_repeat=None, lam=0):
	p_vu = defaultdict(float)
	for (v,u) in av2u_dict:
		if au_dict[v] > 1:
			if av2u_repeat is None:
				p_vu[(int(v),int(u))] = float(av2u_dict[(v,u)]+lam) / (2*lam+au_dict[v]) 
			else:
				p_vu[(int(v),int(u))] = float(av2u_dict[(v,u)]+lam) / (2*lam+au_dict[v]+av2u_repeat[(v,u)])
	return p_vu

def jaccard(G, av2u_dict, au_dict, avnu_dict):
	p_vu = defaultdict(float)
	for (v,u) in av2u_dict:
		v_or_u = au_dict[v]+au_dict[u]- (avnu_dict[(v,u)]+avnu_dict[(u,v)])
		p_vu[(int(v),int(u))] = float(av2u_dict[(v,u)]) / v_or_u
	return p_vu

def evaluate_basic(G, test_data, p_vu, thetas, au_dict):

	curr_action = test_data[0][location_id_idx]
	results_table = set()
	seen_users = set()
	perform = {}
	pv = {}

	TP = defaultdict(int)
	FN = defaultdict(int)
	FP = defaultdict(int)
	TN = defaultdict(int)

	def update_results(results_table, perform, pv, thetas):
		for u in results_table:
			if pv[u] == 0: continue
			for theta in thetas:
				if perform[u] == 1:
					if pv[u] >= theta:
						TP[theta] += 1
					else:
						FN[theta] += 1
				elif perform[u] == 0:
					if pv[u] >= theta:
						FP[theta] += 1
					else:
						TN[theta] += 1

	for row in test_data:
		user = int(row[user_id_idx])
		if au_dict[user] == 1:
			continue
		timestamp = row[timestamp_idx]
		action = row[location_id_idx]
		if action != curr_action:
			# Move to next action
			# pu_list = sorted([pv[u] for u in results_table])
			# print pu_list
			update_results(results_table, perform, pv, thetas)

			curr_action = action
			results_table = set()
			# print Counter(perform.values())
			perform = {}
		if user in seen_users:
			continue
		seen_users.add(user)
		if user in results_table:
			perform[user] = 1
		else:
			results_table.add(user)
			pv[user] = 0
			perform[user] = 2
		user_node = G.GetNI(user)
		for i in xrange(user_node.GetDeg()):
			nbr = user_node.GetNbrNId(i)

			if nbr in results_table:
				pv[nbr] += (1-pv[nbr])*p_vu[(user,nbr)]
			else:
				results_table.add(nbr)
				pv[nbr] = p_vu[(user,nbr)]
				perform[nbr] = 0
	update_results(results_table, perform, pv, thetas)
	return TP, FN, FP, TN

def plot_ROC(TP_l, FN_l, FP_l, TN_l, thetas, name_l):
	
	plt.xlabel("False positive rate")
	plt.ylabel("True positive rate")
	plt.title("ROC Curve for Brightkite probabilities")
	handles = []
	for i in range(len(name_l)):
		TPR = []
		FPR = []
		for theta in thetas:
			TPR.append(float(TP_l[i][theta]) / (TP_l[i][theta] + FN_l[i][theta]))
			FPR.append(float(FP_l[i][theta]) / (FP_l[i][theta] + TN_l[i][theta]))
		next, = plt.plot(FPR, TPR, label=name_l[i])
		handles.append(next)
	# plt.legend(handles)
	plt.legend(handles=handles)
	plt.savefig("ROC_brightkite.png")
	plt.show()

test_savefile = '../data/test_sampled_brightkite.npy'
socialGraphFilename = '../data/Brightkite_edges.txt'
# test_savefile = 'test_small.npy'
# socialGraphFilename = 'small_edges.txt'
user_id_idx = 0
timestamp_idx = 1
location_id_idx = 2

test_data = np.load(test_savefile)
G = snap.LoadEdgeList(snap.PUNGraph, socialGraphFilename)

f = open('../saved_dictionaries/av2u.p', 'r')
av2u_dict = pk.load(f)
f.close()

f = open('../saved_dictionaries/au.p', 'r')
au_dict = pk.load(f)
f.close()

f = open('../saved_dictionaries/avnu.p', 'r')
avnu_dict = pk.load(f)
f.close()

f = open('../saved_dictionaries/av2u_repeat.p', 'r')
av2u_repeat_dict = pk.load(f)
f.close()


theta_step = 0.05
start = 0.0
end = 1.0
thetas = list(np.arange(0.0, 1., 0.05))

p_vu_l = []
name_l = ['bernoulli', 'jaccard']
TP_l, FN_l, FP_l, TN_l = [], [], [], []
# p_vu_l.append(bernoulli(G, av2u_dict, au_dict, None, lam=1))
p_vu_l.append(bernoulli(G, av2u_dict, au_dict, av2u_repeat_dict, lam=0))
p_vu_l.append(jaccard(G, av2u_dict, au_dict, avnu_dict))
for p_vu, n in zip(p_vu_l, name_l):
	f = open('../saved_dictionaries/weights-' + n + '.p', 'w')
	pk.dump(p_vu, f)
	f.close()
	TP, FN, FP, TN = evaluate_basic(G, test_data, p_vu, thetas, au_dict)
	TP_l.append(TP)
	FN_l.append(FN)
	FP_l.append(FP)
	TN_l.append(TN)

plot_ROC(TP_l, FN_l, FP_l, TN_l, thetas, name_l)