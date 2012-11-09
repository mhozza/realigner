

class State:
    def __init__(self):
        return
    
    def durationGenerator(self):
        yield(-1)
        
    def emission(self, X, x, dx):
        return 0.1;

class TableState(State):
    
    emission = dict()
    
    def __init(self):
        return;
    
    def durationGenerator(self):
        yield(1)

    def emission(self, X, x, dx):
        return self.emission[X[x:x+dx]]
    
    
    
class GeneralizedHMM:
    states = list()
    transitions = dict()
    
    def __init__(self):
        self.transitions.setdefault(dict())
        
    def addState(self, state):
        state.setID(len(list))
        list.append(state)
        return len(list) - 1
    
    def addTransition(self, stateFrom, stateTo, probability):
        self.transitions[stateFrom][stateTo] = probability
    
    def getForwardTable(self, X, Y, x, y, dx, dy,
        memoryPattern=None, initialRow=None):
        for