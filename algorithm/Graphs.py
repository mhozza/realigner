"""
This module conatin some basig graph algorithms
"""
from collections import defaultdict

def toposort(graph):
    """
    Sort vertices of graph topologically. "graph" is expected to be two nested 
    dictionaries (second can be list), where vertices are used as keys. 
    """
    states = [x for x in graph]
    out_order = list()
    stack = []
    visited = defaultdict(lambda *_: False)
    for v in states:
        stack.append((v, 0))
        while len(stack) > 0:
            v, s = stack.pop()
            if s == 0:
                if visited[v]:
                    continue
                s = graph[v].__iter__()
            visited[v] = True
            try:
                u = s.next()
                stack.append((v, s))
                stack.append((u, 0))
                continue
            except StopIteration:
                out_order.append(v)
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