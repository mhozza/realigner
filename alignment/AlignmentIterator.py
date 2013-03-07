"""
Several generators of positions used in alignments.
"""

from collections import deque 
from Alignment import Alignment
#import matplotlib.pyplot as pyplot


        
def autoconvDecorator(f):
    def newFunction(*other, **args):
        if not isinstance(other[0], Alignment):
            other = list(other)
            other[0] = Alignment(other[0])
            other = tuple(other)
        return f(*other, **args)
    return newFunction

NegativeInfinity = float("-inf")


def seq_len(sequence):
    return len(sequence) - sequence.count('-')
    
@autoconvDecorator
def AlignmentPositionGenerator(alignment, window=None):
    """
    Generate all positions from alignment. Accepts tuple/list or Alignment
    object for parameter "alignment". "window" parameter is list of tuples
    containing restrictions for each alignment
    """
    if window == None:
        window = [(0, seq_len(x)) for x in alignment.sequences]
    
    start = max(
        [alignment.seq_to_aln[i][window[i][0]] for i in range(len(window))]
    )
    stop  = min(
        [alignment.seq_to_aln[i][window[i][1]] for i in range(len(window))]
    )
    for i in range(start, stop):
        yield tuple([alignment.aln_to_seq[j][i] for j in range(len(window))])    
        

#TODO: add support for more than two sequences
@autoconvDecorator
def AlignmentBeamGenerator(alignment, width = -1, window=None):
    """
    Generator of positions with distance width around input alignment. Works
    ony for two dimmensional alignments now
    """
    if width < 0:
        width = len(alignment.sequences[0])
    if window == None:
        window = [(0, seq_len(x)) for x in alignment.sequences]
    maxY = seq_len(alignment.sequences[1])
    maxX = seq_len(alignment.sequences[0])
    Q = deque()
    pos = [maxX, maxY]
    print(len(pos), len(window))
    larger_window = [
        (
            max(0, window[i][0] - width),
            min(pos[i], window[i][1] + width)
        )
        for i in range(len(window))
    ]
    G = list(AlignmentPositionGenerator(alignment, larger_window))
    G.append((maxX, maxY))
    X = G[0][0]
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
        if X >= window[0][0] and X <= window[0][1]: 
            for i in range(max(
                               0,
                               Q[0][1] - width,
                               window[1][0]),
                           min(
                               maxY + 1,
                               gg[1] + width + 1,
                               window[1][1] + 1)):
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
        if X >= window[0][0] and X <= window[0][1]:
            for i in range(max(0,
                               Q[0][1] - width,
                               window[1][0]),
                           min(maxY + 1,
                               gg[1] + width + 1,
                               window[1][1] + 1)):
                yield((X, i))
        X += 1
        
@autoconvDecorator
def AlignmentFullGenerator(alignment, _ = -1):
    """
    Generate iterator over all possible combination of positions in sequences
    from input alignment.
    """
    maxX = seq_len(alignment.sequences[0])
    maxY = seq_len(alignment.sequences[1])
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
    def visualize():
        """
        Test function
        """
        #=======================================================================
        # A = TextAlignmentToTupleList("ACGTGCTAC---GATCGAG---CTATCGACGATCGACGATCGA---CGGAGCGACTACT--------AGCTAGCTGATCGAT", "ACGTGCTACAGCTA----GGCTATATCGACG-----CGATCAGCTTTTT---TTTTTCTGCATCGACGTACG---GATCGAT")
        # maxX = len([a[0] for a in A if a[0] != '-'])
        # maxY = len([a[1] for a in A if a[1] != '-'])
        # fig = pyplot.figure()
        # ax  = fig.add_subplot(111)
        # (X, Y) = unzipList(AlignmentPositionGenerator(A))
        # ax.plot(X, Y, "-")
        # ax.grid(True)
        # width = 2
        # (X, Y) = unzipList(AlignmentBeamGenerator(A, width))    
        # ax.plot(X, Y, "o", color="red")
        # X = []
        # Y = []
        # a = list(AlignmentPositionGenerator(A))
        # #a.append((maxX, maxY))
        # for x in a:
        #    for i in range(-width, width+1):
        #        for j in range(-width, width+1):
        #            if x[0] + i < 0 or \
        #               x[1] + j < 0 or \
        #               x[0] + i > maxX or \
        #               x[1] + j > maxY:
        #                continue
        #            X.append(x[0]+i+0.2)
        #            Y.append(x[1]+j)
        # ax.plot(X, Y, "o", color="green")
        # pyplot.show()
        #=======================================================================
    visualize()    
    
