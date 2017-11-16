#!/usr/bin/python

import snap
import influence_set

def main():
    G = snap.TNGraph.New()
    for i in range(1, 9):
        G.AddNode(i)

    weights = {}
    G.AddEdge(1, 2)
    weights[(1, 2)] = 0.5

    G.AddEdge(1, 3)
    weights[(1, 3)] = 0.5

    G.AddEdge(2, 3)
    weights[(2, 3)] = 0.5

    G.AddEdge(2, 4)
    weights[(2, 4)] = 0.5

    G.AddEdge(3, 1)
    weights[(3, 1)] = 0.5

    G.AddEdge(3, 5)
    weights[(3, 5)] = 0.5

    G.AddEdge(3, 7)
    weights[(3, 7)] = 0.5

    G.AddEdge(4, 3)
    weights[(4, 3)] = 0.5

    G.AddEdge(5, 3)
    weights[(5, 3)] = 0.5

    G.AddEdge(6, 3)
    weights[(6, 3)] = 0.5

    G.AddEdge(6, 7)
    weights[(6, 7)] = 0.5

    G.AddEdge(7, 8)
    weights[(7, 8)] = 0.5

    for key in weights.keys():
        weights[key] = 0.5
        
    weights[(1, 2)] = 0.5
    numTrials = 100000
    averageSize = 0.0
    initialSet = set([1, 6])
    for i in range(0, numTrials):
        influenceSet = influence_set.getAnInfluenceSet(G, weights, initialSet)
        averageSize += len(influenceSet) / float(numTrials)
        #print influenceSet
        
    print "Average size for set " + str(initialSet) + " is " + str(averageSize)
    print "Average size for set " + str(initialSet) + " is " + str(influence_set.computeAverageInfluenceSetSize(G, weights, initialSet, numTrials))
    
    
if __name__ == "__main__":
    main()