import snap
import matplotlib.pyplot as plt
import cPickle as pk


# Computes and returns F1 score with respect to
# edges in G and in G_prime
#
# TP = edge in G, edge in G_prime
# FN = edge in G, edge not in G_prime
# FP = edge not in G, edge in G_prime
# TN = edge not in G, edge not in G_prime (not needed)
def compare_true_versus_inferred(G, G_prime):
    assert G.GetEdges() > 0 or G_prime.GetEdges() > 0  # Avoid division by 0

    # Compute TP and FN
    TP = 0.0
    FN = 0.0
    for edge in G.Edges():
        nodeId1, nodeId2 = edge.GetId()
        if G_prime.IsEdge(nodeId1, nodeId2):
            TP += 1.0
        else:
            FN += 1.0
    
    # Compute FP
    FP = 0.0
    for edge in G_prime.Edges():
        nodeId1, nodeId2 = edge.GetId()
        if not G.IsEdge(nodeId1, nodeId2):
            FP += 1.0
    
    try:
        precision = TP / (TP + FP)
        recall = TP / (TP + FN)
    except: 
        return 0

    F1_score = 2.0 * TP / (2 * TP + FN + FP)
    print "TP: {}, FN: {}, FP: {}".format(TP, FN, FP)
    print "Precision: {}, Recall: {}".format(precision, recall)
    print "F1 score: {}".format(F1_score)
    return F1_score


def plot_threshold_against_f1(G, weights, steps, name):
    thresholds = []
    f1_scores = []
    G_prime = edit_graph(weights, None, 0.0)
    for i in range(0, steps):
        threshold = i / float(steps)
        G_prime = edit_graph(weights, G_prime, threshold)
        f1_score = compare_true_versus_inferred(G, G_prime)
        
        thresholds.append(threshold)
        f1_scores.append(f1_score)
    
    plt.title("F1 Score Distribution for Thresholds")
    plt.xlabel("Thresholds")
    plt.ylabel("F1 Score (2TP / (2TP + FN + FP))")
    plt.plot(thresholds, f1_scores)
    plt.savefig("{}_f1_score_dist.png".format(name))
    plt.show()

def edit_graph(weights, G, threshold):
    assert 0 <= threshold < 1

    if G is None:
        G = snap.TUNGraph.New()
        for (u,v) in weights:
            if not G.IsNode(u):
                G.AddNode(u)
            if not G.IsNode(v):
                G.AddNode(v)
            if weights[(u,v)] >= threshold and not G.IsEdge(u,v):
                G.AddEdge(u,v)
        return G

    else:
        edges_to_delete = set()
        for edge in G.Edges():
            u, v = edge.GetId()
            if weights[(u,v)] < threshold and weights[(v,u)] < threshold:
                edges_to_delete.add((u,v))
        for u,v in edges_to_delete:
            G.DelEdge(u,v)
        return G

slice_name = '../data/sliced_graph.txt'
weights_name = '../saved_dictionaries/weights-bernoulli.p'
f = open(weights_name, 'r')
G = snap.LoadEdgeList(snap.PUNGraph, slice_name)
weights = pk.load(f)
f.close()

plot_threshold_against_f1(G, weights, 50, 'sliced')