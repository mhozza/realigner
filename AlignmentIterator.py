"""
Several generators of positions used in alignments.
"""

from collections import deque 
import matplotlib.pyplot as pyplot

def TextAlignmentToTupleList(X, Y):
    """
    Convert alignment to list of tuples (like zip)
    """
    return [(X[ii], Y[ii]) for ii in range(len(X)) if ii < len(Y)]
    

def AlignmentPositionGenerator(Alignment):
    """
    Generate all positions form alignment
    """
    Xlen = -1
    Ylen = -1
    #yield((Xlen, Ylen))
    for (X, Y) in Alignment:
        if Y != '-':
            Ylen += 1
        if X != '-':
            Xlen += 1
        #else:
        #    continue # If there is no move at X, we do not yield
        yield((Xlen, Ylen))
        

def AlignmentBeamGenerator(Alignment, width = -1):
    """
    Generator of positions with distance width around input alignment
    """
    if width < 0:
        width = len(Alignment)
    Q = deque()
    G = AlignmentPositionGenerator(Alignment)
    maxY = len([A[1] for A in Alignment if A[1] != '-'])
    X = 0
    for g in G:
        Q.append(g)
        if X + width >= g[0]:
            continue
        while len(Q) > 0 and X - width > Q[0][0]:
            Q.popleft()
        if len(Q) > 1: 
            gg = Q[-2]
        else:
            gg = g 
        for i in range(max(0, Q[0][1] - width), min(maxY, gg[1] + width + 1)):
            yield((X, i))
        X += 1
    if len(Q) == 0:
        return 
    g = Q[-1]
    while len(Q) > 0 and Q[-1][0] >= X:
        while len(Q) > 0 and X - width > Q[0][0]:
            Q.popleft()
        if len(Q) <= 0:
            break
        if len(Q) > 1:
            gg = Q[-2]
        else: 
            gg = g
        for i in range(max(0, Q[0][1] - width), min(maxY, gg[1] + width + 1)):
            yield((X, i))
        X += 1
        
def FullAlignmentGenerator(Alignment, _ = -1):
    """
    Generate iterator over all possible combination of positions in sequences
    from input alignment.
    """
    maxX = len([A[0] for A in Alignment if A[0] != '-'])
    maxY = len([A[1] for A in Alignment if A[1] != '-'])
    for i in range(0, maxX):
        for j in range(0, maxY):
            yield((i, j))
 
def unzipList(List):
    """
    Unzip list: [(x1, y1), (x2, y2), (x3, y3)] -> ([x1, x2, x3], [y1, y2, y3])
    """
    X = []
    Y = []
    for a in List:
        X.append(a[0])
        Y.append(a[1])
    return (X, Y)
        
if __name__ == "__main__":
    def main():
        """
        Test function
        """
        A = TextAlignmentToTupleList("ACG--C-A--CA-C", "AC-TGGGAC-CACC")
        maxX = len([a[0] for a in A if a[0] != '-'])
        maxY = len([a[1] for a in A if a[1] != '-'])
        fig = pyplot.figure()
        ax  = fig.add_subplot(111)
        (X, Y) = unzipList(AlignmentPositionGenerator(A))
        ax.plot(X, Y, "-")
        ax.grid(True)
        width = 2
        (X, Y) = unzipList(AlignmentBeamGenerator(A, width))    
        ax.plot(X, Y, "o", color="red")
        X = []
        Y = []
        a = AlignmentPositionGenerator(A)
        for x in a:
            for i in range(-width, width+1):
                for j in range(-width, width+1):
                    if x[0] + i < 0 or \
                       x[1] + j < 0 or \
                       x[0] + i >= maxX or \
                       x[1] + j >= maxY:
                        continue
                    X.append(x[0]+i+0.2)
                    Y.append(x[1]+j)
        ax.plot(X, Y, "o", color="green")
        pyplot.show()
    main()    
    