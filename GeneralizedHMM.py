import MemoryPatterns
from collections import defaultdict
from HMM import State, HMM
    
class GeneralizedState(State):
    
    def __init(self):
        State.__init__(self)
        self.durations = [] 
        
        
    def load(self, dictionary):
        State.load(self, dictionary)
        if "durations" not in dictionary:
            raise "durations were not found in GeneralizedState"
        self.durations = list(dictionary["durations"])
        
        
    def toJSON(self):
        ret = State.toJSON(self)
        ret["durations"] = self.durations
        return ret        
        
    
    def durationGenerator(self):
        for x in self.durations:
            yield(x)


    def emission(self, X, x, dx):
        return self.emission[X[x:x+dx]]
    
    
    
class GeneralizedHMM(HMM):
           
    def getForwardTable(self, X, x, dx, memoryPattern=None, initialRow=None):
        
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx)
            
        rows = [defaultdict(float) for x in range(dx)]
        
        ignoreFirstRow = False
        if initialRow != None:
            rows[0] = initialRow
            ignoreFirstRow = True
        else:
            for state in self.states:
                rows[0][(state.getStateID, 0)] = state.getStartProbability()
        
        # Main algorithm
        retTable = list()
        for _x in range(dx):
            if ignoreFirstRow and _x == 0:
                continue
            for (stateID, _dx) in rows[_x]:
                state = self.states[stateID]
                for followingID in state.followingIDs():
                    following = self.states[followingID]
                    for (_sdx, dprob) in state.durationGenerator():
                        rows[_x + _dx][(followingID, _sdx)] += \
                            following.emission(X, x + _x + _dx, _sdx) \
                            * self.transitions[stateID][followingID] * dprob
                
            if memoryPattern.next():
                retTable.append((_x, rows[_dx]))
            rows[_dx] = list()
                
        return retTable
    
    def getBackwardTable(self, X, x, dx, memoryPattern=None, initialRow=None):
        
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx)
            
        rows = [defaultdict(float) for x in range(dx)]
        
        ignoreFirstRow = False
        if initialRow != None:
            rows[dx] = initialRow
            ignoreFirstRow = True
        else:
            for state in self.states:
                rows[dx][(state.getStateID, 0)] = state.getEndProbability()
        
        # Main algorithm
        retTable = list()
        for _x in reversed(list(range(dx + 1))):
            if ignoreFirstRow and _x == dx:
                continue
            for (stateID, _dx) in rows[_x]:
                state = self.states[stateID]
                for previousID in state.previousIDs():
                    previous = self.states[previousID]
                    for (_sdx, dprob) in previous.durationGenerator():
                        rows[_x - _sdx][(previousID, _sdx)] += \
                            state.emission(X, x + _x, _dx) \
                            * self.transitions[previousID][stateID] * dprob
                
            if memoryPattern.next():
                retTable.append((_x, rows[_dx]))
            rows[_dx] = list()
                
        return retTable
    
    
    # TODO: check if this even works
    def getProbability(self, X, x, dx, positionGenerator = None): 
        table = self.getForwardTable(X, x, dx, 
                                     memoryPattern=MemoryPatterns.last(dx))
        return sum([i * self.states[stateID].getEndProbability() 
                    for ((stateID, _), i) in table[0][1]])
    