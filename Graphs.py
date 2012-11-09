from collections import defaultdict
# This module contain some basic graph algorithms

#TODO test this 
def toposort(graph):
    states = [x for x in graph]
    visited = defaultdict(bool)
    for state in states:
        visited[state] = False
    order = list()
    def __toposort(v):
        if visited[v]:
            return
        visited[v] = True
        for u in graph[v]:
            __toposort(u)
        order.append(v)
    map(__toposort, states)
    return order

def orderToDict(order):
    ret = dict()
    for index in range(len(order)):
        ret[order[index]] = index
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