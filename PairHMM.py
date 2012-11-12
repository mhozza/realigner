# TODO: start writing docstring!
# TODO: start writing unittests!

import MemoryPatterns
from collections import defaultdict
from GeneralizedHMM import GeneralizedState
from HMM import HMM

class GeneralizedPairState(GeneralizedState):
        
    def load(self, dictionary):
        GeneralizedState.load(self, dictionary)
        newemi = defaultdict(self.mathType)
        for (key, val) in self.emissions.iteritems():
            newemi[tuple(key)] = val
        self.emissions = newemi
        for d in range(len(self.durations)):
            self.durations[d] = (tuple(self.durations[d][0]),
                                    self.durations[d][1])
       
        
    def emission(self, X, Y, x, y, dx, dy):
        return self.emissions[(X[x : x + dx], Y[y : y + dy])]
        

class GeneralizedPairHMM(HMM):

    # TODO: este pridat dalsie restrikcie z anotacie
        
    
    def setAnnotations(self):
        return
   
    
    # Returns forward table. We can specify memory pattern, position generator
    # and initial row. Compatible with memory preserving tricks 
    # TODO: +-1
    # TODO: allow restrictions 
    def getForwardTable(self, X, Y, x, y, dx, dy,
        memoryPattern = None, positionGenerator = None, initialRow = None):
        # Default position generator
        if positionGenerator == None:
            positionGenerator = \
                ((i,j) for i in range(dx + 1) for j in range(dy + 1))
        
        # Default memory pattern (everything)
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx)
            return
        
        # Initialize table
        rows = [defaultdict(lambda *_:defaultdict(self.mathType)) for _ in range(dx+1)]
        
        # Initialize first row
        ignoreFirstRow = False
        if initialRow != None:
            rows[0] = initialRow
            ignoreFirstRow = True
        else:
            for state in self.states:
                rows[0][0][(state.getStateID(), 0, 0)] = \
                    state.getStartProbability()
        
        # Main algorithm
        _x_prev = -1000000 
        retTable = list()
        for (_x, _y) in positionGenerator:
            if ignoreFirstRow and _x == 0: #BUG: ak ignorujem prvy riadok, pokazi sa mi zapamatavanie
                continue
            for (stateID, _dx, _dy) in rows[x + _x][y + _y].iteritems():
                state = self.states[stateID]
                for followingID in state.followingIDs():
                    following = self.states[followingID]
                    for ((_sdx, _sdy), dprob) in state.durationGenerator():
                        rows[_x + _dx][_y + _dy][(following, _sdx, _sdy)] += \
                            following.emission(
                                X, 
                                Y, 
                                x + _x + _dx, 
                                y + _y + _dy, 
                                _sdx, 
                                _sdy
                            ) * self.transitions[stateID][followingID] * dprob
            # If rows were changed, remember it
            if _x_prev != _x:
                if memoryPattern.next():
                    retTable.append((x + _x, rows[_x_prev]))
                rows[_x_prev] = list()
            _x_prev = _x
        
        # Remember last row if necessary
        if memoryPattern.next():
            retTable.append((x + _x_prev, rows[dx]))   
        
        # Finally, done:-)
        return retTable
    
    
    # Basically copy of the getForwardTable. Might share bugs
    # TODO: +- 1
    # TODO: restrictions
    # TODO: reverse memory pattern?
    def getBackwardTable(self, X, Y, x, y, dx, dy,
        memoryPattern = None, positionGenerator = None, initialRow = None):
        # Default position generator
        if positionGenerator == None:
            positionGenerator = \
                ((i,j) for i in range(dx + 1) for j in range(dy + 1))
        # Some generators have to be reversed
        positionGenerator = reversed(list(positionGenerator))
        
        # Default memory pattern (everything)
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx)
        
        # Initialize table
        rows = [defaultdict(lambda *_:defaultdict(self.mathType)) for _ in range(dx+1)]
        
        # Initialize first row
        ignoreFirstRow = False
        if initialRow != None:
            rows[dx] = initialRow
            ignoreFirstRow = True
        else:
            for state in self.states:
                rows[dx][dy][state.getStateID(), 0, 0] = \
                    state.getEndProbability()
        
        # Main algorithm
        _x_prev = x + dx + 100000
        retTable = list()
        for (_x, _y) in positionGenerator:
            if ignoreFirstRow and _x == dx:
                continue
            for (stateID, _dx, _dy) in rows[x + _dx][y + _dy].iteritems():
                state = self.states[stateID]
                for previousID in state.previousIDs():
                    previous = self.states[previousID]
                    for ((_sdx, _sdy), dprob) in previous.durationGenerator():
                        rows[_x - _sdx][_y - _sdy][(previous, _sdx, _sdy)] = \
                            previous.emission(
                                X,
                                Y,
                                x + _x,
                                x + _y,
                                _dx,
                                _dy
                            ) * self.transitions[previousID][stateID] * dprob
            
            # Remember last row if necessary
            if _x_prev != _x:
                if memoryPattern.next():
                    retTable.append((x + _x, rows[_x_prev]))
                rows[_x_prev] = list()  
            _x_prev = _x
        
        # Remember last row if necessary
        if memoryPattern.next():
            retTable.append((x + _x_prev, rows[0]))
                             
        # Finally, done:-)
        return retTable
    
    
    def getViterbiTable(self, X, Y, x, y, dx, dy):
        return
    
    
    def getViterbiAlignment(self, table):
        return
    
    
    def getProbability(self, X, Y, x, y, dx, dy, positionGenerator = None):
        table = self.getForwardTable(X, Y, x, y, dx, dy, 
                                     memoryPattern=MemoryPatterns.last(dx),
                                     positionGenerator=positionGenerator)
        return sum([i * self.states[stateID].getEndProbabilit()
                    for (stateID, i) in table[0][1][dy]])
    
    
    def getPosteriorTable(self, X, Y, x, y, dx, dy, 
                          forwardTable = None, backwardTable = None,
                          positionGenerator = None):
        # Najskor chcem taku, co predpoklada ze obe tabulky su velke
        # Potom chcem taku, ktora si bude doratavat chybajuce
        # Potom pridat switch, ktory mi umozni robit optimalizacie.
        # Ale potom bude treba vediet, ci ist od predu, alebo od zadu
        
        # Fetch tables if they are not provided
        if forwardTable == None:
            forwardTable = self.getForwardTable(X, Y, x, y, dx, dy,
                positionGenerator=positionGenerator)
        if backwardTable == None:
            backwardTable = self.getBackwardTable(X, Y, x, y, dx, dy,
                positionGenerator=positionGenerator)

        # Sort tables by first element (just in case)    
        sorted(forwardTable,key=lambda (x,_) : x)
        sorted(backwardTable,key=lambda (x,_) : x)
        
        # Compute posterior probabilities
        retTable = list()
        for (index, column) in forwardTable:
            backward_column = backwardTable[index]
            ret = defaultdict(lambda *_:defaultdict(self.mathType(0.0)))
            for (colindex, value) in column:
                for triple in value:
                    ret[colindex][triple] = column[colindex][triple] * \
                        backward_column[colindex][triple]
            retTable.append((index, ret)) 

        return retTable