#!/usr/bin/python

import snap
import random
from collections import defaultdict
from heapq import *
import numpy as np

# Parameters:
# - G: TNGraph
# - weights: map of edges in G to associated weight
# - nodeIds: set of IDs of nodes we are interested
# - defaultWeight: the weight of an edge if not found in weights
#
# Returns:
# - one possible influence set of the "nodeIds" based
#   on the weights of each edge
def getAnInfluenceSet(G, weights, nodeIds, defaultWeight=0.0):
    influenceSet = set(nodeIds)
    scheduled = set(nodeIds)
    
    while len(scheduled) > 0:
        randomNodeId = scheduled.pop()  # Doesn't matter how nodes are scheduled to influence
        if G is None:
            if randomNodeId not in weights:
                continue
            for v in weights[randomNodeId]:
                if v in influenceSet:
                    continue
                probOfInfluence = weights[randomNodeId][v]
                trial = random.random()
                if trial < probOfInfluence:
                    scheduled.add(v)
                    influenceSet.add(v)
        else:
            if not G.IsNode(randomNodeId): #why? something about blind greedy is broken, thats why
                continue
            randomNode = G.GetNI(randomNodeId)
            for i in range(0, randomNode.GetOutDeg()):
                neighborNodeId = randomNode.GetOutNId(i)
                if neighborNodeId in influenceSet:  # Each node can only be influenced and scheduled once
                    continue
                
                probOfInfluence = weights.get((randomNodeId, neighborNodeId), defaultWeight)
                trial = random.random()
                if trial < probOfInfluence:
                    scheduled.add(neighborNodeId)
                    influenceSet.add(neighborNodeId)
            
    return influenceSet

    
# Parameters:
# - G: TNGraph
# - weights: map of edges in G to associated weight
# - nodeIds: set of IDs of nodes we are interested
# - numTrials: number of trials to average over
# - defaultWeight: the weight of an edge if not found in weights
#
# Returns:
# - average of influence set size across "numTrials" iterations
def computeAverageInfluenceSetSize(G, weights, nodeIds, numTrials, defaultWeight=0.0, verbose=False):
    gain_list = []
    averageSize = 0.0
    for i in range(0, numTrials):
        gain = len(getAnInfluenceSet(G, weights, nodeIds, defaultWeight))
        averageSize += gain
        gain_list.append(gain)
    if verbose and len(gain_list) > 1:
        print "With {} trials and {} node: mean = {}, std_dev = {}". \
                format(numTrials, len(nodeIds), np.mean(gain_list), np.std(gain_list))
    return averageSize / float(numTrials)

#greedy hill climbing algorithm
def hill_climb(G, weights, k, num_trials=100):
    assert k < G.GetNodes()
    S = list()
    for i in range(k):
        print "Finding node {} to add to influence set".format(i)
        best_size = -1
        best_node_id = None
        for node in G.Nodes():
            node_id = node.GetId()
            if node_id in S:
                continue
            S_prime = set(S).union(set([node_id]))
            infl_set_size = computeAverageInfluenceSetSize(G, weights, S_prime, num_trials)
            if infl_set_size > best_size:
                best_size = infl_set_size
                best_node_id = node_id
        S.append(best_node_id)
    return S

def CELF(G, weights, k, num_trials=100):
    S = []
    Q = []
    print "Entering CELF algorithm"
    if G is None:
        print "Number of nodes in weights: {}".format(len(weights))
        for u in weights:
            u_mg = computeAverageInfluenceSetSize(None, weights, set([u]), num_trials)
            u_updated = 0
            heappush(Q, (-u_mg, u, u_updated)) #push the negative marginal gain since heappush is min heap implementation
    else:
        for node in G.Nodes():
            u = node.GetId()
            u_mg = computeAverageInfluenceSetSize(G, weights, set([u]), num_trials)
            u_updated = 0
            heappush(Q, (-u_mg, u, u_updated)) #push the negative marginal gain since heappush is min heap implementation
    f_S = 0
    while len(S) < k:
        u_mg, u, u_updated = heappop(Q)
        if u_updated == len(S):
            S.append(u)
            f_S -= u_mg #u_mg is the negative marginal gain
            print "Found node {} in influence set".format(len(S))
        else:
            u_mg = computeAverageInfluenceSetSize(G, weights, set(S).union(set([u])), num_trials) - f_S
            u_updated = len(S)
            heappush(Q, (-u_mg, u, u_updated))
    return S