#!/usr/bin/python

import snap
import random


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
def computeAverageInfluenceSetSize(G, weights, nodeIds, numTrials, defaultWeight=0.0):
    averageSize = 0.0
    for i in range(0, numTrials):
        averageSize += len(getAnInfluenceSet(G, weights, nodeIds, defaultWeight)) / float(numTrials)
    
    return averageSize
