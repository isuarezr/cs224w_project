import snap

def compare_true_versus_inferred(G, G_prime):
	pass

def infer_graph(weights, threshold):
	assert 0 <= threshold < 1
	G = snap.TUNGraph.New()

	for (u,v) in weights:
		if not G.IsNode(u):
			G.AddNode(u)
		if not G.IsNode(v):
			G.AddNode(v)
		if weights[(u,v)] >= threshold and not G.IsEdge(u,v):
			G.AddEdge(u,v)
	return G
