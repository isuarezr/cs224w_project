import snap


# Computes and returns F1 score with respect to
# edges in G and in G_prime
#
# TP = edge in G, edge in G_prime
# FN = edge in G, edge not in G_prime
# FP = edge not in G, edge in G_prime
# TN = edge not in G, edge not in G_prime (not needed)
def compare_true_versus_inferred(G, G_prime):
    assert G.GetEdges() > 0 and G_prime.GetEdges() > 0  # Avoid division by 0

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
            TN += 1.0
    
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    F1_score = 2.0 * TP / (2 * TP + FN + FP)
    #print "TP: {}, FN: {}, FP: {}".format(TP, FN, FP)
    #print "Precision: {}, Recall: {}".format(precision, recall)
    return F1_score

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