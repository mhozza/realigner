"""
This module conatin some basig graph algorithms
"""
from collections import defaultdict

def toposort(graph):
    """
    Sort vertices of graph topologically. "graph" is expected to be two nested 
    dictionaries, where vertices are used as keys. 
    """
    states = [x for x in graph]
    visited = defaultdict(bool)
    for state in states:
        visited[state] = False
    out_order = list()
    def __toposort(v):
        if visited[v]:
            return
        visited[v] = True
        if v in graph:
            for u in graph[v]:
                __toposort(u)
        out_order.append(v)
    map(__toposort, states)
    return out_order

def orderToDict(permutation):
    """
    Change permutation into dictionary.
    """
    ret = dict()
    permutation = list(permutation)
    for index in range(len(permutation)):
        ret[permutation[index]] = index
    return ret

if __name__ == "__main__":
    G = defaultdict(dict)
    G[0][3] = 1
    G[1][2] = 1
    G[1][5] = 1
    G[2][3] = 1
    G[4][3] = 1
    G[4][5] = 1
    G[5][9] = 1
    G[6][5] = 1
    G[6][14] = 1
    G[7][10] = 1
    G[8][13] = 1
    G[9][10] = 1
    G[10][6] = 1
    G[12][13] = 1
    G[13][11] = 1
    G[13][14] = 1
    G[14][8] = 1
    print(G)
    order = toposort(G)
    print(order)