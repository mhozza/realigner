# TODO: start writing docstring!
# TODO: start writing unittests!

# TODO: Create single models

import MemoryPatterns
from collections import defaultdict

class PairState:
    def __init__(self):
        return
    
    def durationGenerator(self):
        yield((-1,-1))
        
    def emission(self, X, Y, x, y, dx, dy):
        return 0.1;
    
class PairTableState(PairState):
    
    emission = dict()
    
    def __init__(self):
        #TODO: load it from something
        return
    
    def durationGenerator(self):
        yield((1,1,1))

    def emission(self, X, Y, x, y, dx, dy):
        return self.emission[(X[x:x+dx],Y[y:y+dy])]
    
class PairRepeatState(PairState):
    
    def __init__(self):
        return
    
    def durationGenerator(self):
        for i in range(1,10000):
            for j in range(0,i):
                yield(((j,i-j),0.001)) # now for some trivial distribution
        
    def emission(self, X, Y, x, y, dx, dy):
        self.hmm.getProbability(X, Y, x, y, dx, dy)
        # vyrobime HMM, vypocitame hodnotu a zacachujeme ju, lebo ju budeme 
        # mozno neskor znova potrebovat
        # TODO: pridaj aj hashovanie a memoizaciu, nech nekonstruujem tie iste 
        # objekty viac krat -- na to by sa mozno hodila nejaka factory       
        

class GeneralizedPairHMM:
    
    # TODO: este pridat dalsie restrikcie z anotacie
    
    states = list()
    transitions = dict()
    
    def __init__(self):
        self.transitions.setdefault(dict());
    
    # Pridame stav, vrati sa nam jeho idcko
    def addState(self, state):
        state.setID(len(list))
        list.append(state)
        return len(list) - 1
    
    def addTransition(self, stateFrom, stateTo, probability):
        self.transitions[stateFrom][stateTo] = probability
        
    def optimize(self):
        # Vyrobi potrebne tabulky, aby sme vedeli rychlo pocitat
        self.__transitions = list()
        self.__reverse_transitions = list()
        for _ in range(len(self.states)):
            self.__transitions.append(list())
            self.__reverse_transitions.append(list())    
        
    
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
        rows = [defaultdict(lambda *_:defaultdict(float)) for _ in range(dx+1)]
        
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
        rows = [defaultdict(lambda *_:defaultdict(float)) for _ in range(dx+1)]
        
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
                                     memoryPattern=MemoryPatterns.last(dx))
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
            ret = defaultdict(lambda *_:defaultdict(0.0))
            for (colindex, value) in column:
                for triple in value:
                    ret[colindex][triple] = column[colindex][triple] * \
                        backward_column[colindex][triple]
            retTable.append((index, ret)) 

        return retTable