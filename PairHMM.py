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
        

class PairHMM:
    
    states = list()
    transitions = dict()
    
    def __init__(self):
        self.transitions.setdefault(dict());
        return
    
    #Pridame stav, vrati sa nam jeho idcko
    def addState(self, state):
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
    
    def getForwardTable(self, X, Y, x, y, dx, dy, memoryPattern = None):
        return
    
    def getProbability(self, X, Y, x, y, dx, dy):
        # Zbehne forward algoritmus
        return
        
    def getBackwardTable(self, X, Y, x, y, dx, dy):
        return