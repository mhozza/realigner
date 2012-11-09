import MemoryPatterns
from collections import defaultdict
from itertools import product

class State:
    def __init__(self):
        return
    
    def durationGenerator(self):
        yield((-1,-1))
        
    def emission(self, X, Y, x, y, dx, dy):
        return 0.1;
    
class TableState(State):
    
    emission = dict()
    
    def __init__(self):
        #TODO: load it from something
        return
    
    def durationGenerator(self):
        yield((1,1,1))
    
    def emission(self, X, Y, x, y, dx, dy):
        return self.emission[(X[x:x+dx],Y[y:y+dy])]
    
class RepeatState(State):
    
    def __init__(self):
        return
    
    def durationGenerator(self):
        for i in range(1,10000):
            for j in range(0,i):
                yield((j,i-j,0.001)) # now for some trivial distribution
        
    def emission(self, X, Y, x, y, dx, dy):
        self.hmm.getProbability(X, Y, x, y, dx, dy)
        # vyrobime HMM, vypocitame hodnotu a zacachujeme ju, lebo ju budeme mozno neskor znova potrebovat
        #TODO: pridaj aj hashovanie a memoizaciu, nech nekonstruujem tie iste objekty viac krat -- na to by sa mozno hodila nejaka factory       
        

class GeneralizedPairHMM:
    
    #TODO: este pridat dalsie restrikcie z anotacie
    
    states = list()
    transitions = dict()
    
    def __init__(self):
        self.transitions.setdefault(dict());
        return
    
    #Pridame stav, vrati sa nam jeho idcko
    def addState(self, state):
        state.setID(len(list))
        list.append(state)
        return len(list) - 1
    
    def addTransition(self, stateFrom, stateTo, probability):
        self.transitions[stateFrom][stateTo] = probability
        
    def optimize(self):
        #vyrobi potrebne tabulky, aby sme vedeli rychlo pocitat
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
        rows = [defaultdict(lambda *_:defaultdict(int)) for _ in range(dx+1)]
        
        # Initialize first row
        ignoreFirstRow = False
        if initialRow != None:
            rows[0] = initialRow
            ignoreFirstRow = True;
        else:
            for state in self.states:
                rows[0][0][(state.getStateID(),0,0)] = \
                    state.getStartProbability()
        
        # Main algorithm
        _x_prev = -1000000 
        retTable = list()
        for (_x, _y) in positionGenerator:
            if ignoreFirstRow and _x == 0:
                continue
            for (stateID, _dx, _dy) in rows[x + _x][y + _y].iteritems():
                state = self.states[stateID]
                for followingID in state.followingIDs():
                    following = self.states[followingID]
                    for (_sdx, _sdy) in state.durationGenerator():
                        rows[_x + _dx][_y + _dy][(following, _sdx, _sdy)] += \
                            following.emission(
                                X, 
                                Y, 
                                x + _x + _dx, 
                                y + _y + _dy, 
                                _sdx, 
                                _sdy
                            ) * self.transitions[stateID][followingID]
            # If rows were changed, remember it
            if _x_prev != _x:
                if memoryPattern.next():
                    retTable.append((x + _x, rows[_x]))
                rows[_x] = list()
            _x_prev = _x
        
        # Remember last row if necessary
        if memoryPattern.next():
            retTable.append((x + _x_prev, rows[_x]))   
        
        # Finally, done:-)
        return retTable
    
    def getBackwardTable(self, X, Y, x, y, dx, dy):
        return
    
    def getProbability(self, X, Y, x, y, dx, dy, positionGenerator):
        table = self.getForwardTable(X, Y, x, y, dx, dy, 
                                     memoryPattern=MemoryPatterns.last(dx))
        return sum([i for (_,i) in table[0][1][dy]])
            
    