'''
Created on Jan 17, 2013

@author: mic
'''
from repeats.RepeatRealigner import RepeatRealigner
from collections import defaultdict
from algorithm.LogNum import LogNum
from tools import perf

class RepeatRealignerNoBlocks(RepeatRealigner):
    '''
    classdocs
    '''
    
    def __init__(self):
        """
        Constructor
        """
        RepeatRealigner.__init__(self)
    
    @perf.runningTimeDecorator
    def prepareData(self, *data):
        data = RepeatRealigner.prepareData(self, *data)
        ignore_states = self.args.ignore_states
        resolve_indels = self.args.resolve_indels
        arguments = 0
       
        statefun = lambda x: x
        if ignore_states:
            statefun = lambda x: 0
        # Smooth out the data
        table = [defaultdict(lambda *_:defaultdict(self.mathType))
                 for _ in range(len(self.posteriorTable))]
        for x in range(len(self.posteriorTable)):
            for y, dct in self.posteriorTable[x].iteritems():
                for (state, _sdx, _sdy), prob in dct.iteritems():
                    if max(_sdx, _sdy) <= 1:
                        table[x][y][(statefun(state), _sdx, _sdy)] += prob
                        continue
                    len_x, len_y = _sdx, _sdy
                    iter_x = list(range(_sdx))
                    if len_x >= 1:
                        len_x = 1
                    else:
                        iter_x = [0]
                    iter_y = list(range(_sdy))
                    if len_y >= 1:
                        len_y = 1
                    else:
                        iter_y = [0]
                    for xx in iter_x:
                        if x + xx >= len(table):
                            continue
                        for yy in iter_y:
                            table[x - xx][y - yy][(statefun(state), len_x, len_y)] += prob
                            if resolve_indels: 
                                if len_y > 0:
                                    table[x - xx][y - yy][(statefun(state), len_x, 0)] += prob
                                if len_x > 0:
                                    table[x - xx][y - yy][(statefun(state), 0, len_y)] += prob
        self.posteriorTable = table 
        self.drawer.add_posterior_table(self.posteriorTable)
        return data[arguments:]
