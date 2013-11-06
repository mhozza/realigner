import sys
import pylab
print 'ahoj'

graph = dict()

for line in sys.stdin:
    print line
    line = line.strip().split(' ')
    what = line[0]
    data = map(lambda x: 100.0 - float(x), line[1:])
    graph[what] = data

r = range(1, len(graph['simpleModelViterbi']) + 1)

l = pylab.plot(r, graph['simpleModelViterbi'], 'k-', r, graph['repeatRealignerBrona'], 'k--',r,  graph['sff_block_cor'], 'k-.', markerfacecolor='green')
pylab.xlabel('distance from repeat')
pylab.ylabel('% error')
pylab.legend(('3-state Viterbi', 'SFF marginalized', 'SFF block'),
           'upper right', shadow=True, fancybox=True)
pylab.show()
print graph


