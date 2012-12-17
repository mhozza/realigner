from algorithm import MemoryPatterns
from collections import defaultdict
from hmm.HMM import State, HMM
from tools.Exceptions import ParseException
import operator
    
class GeneralizedState(State):
       
    def __init__(self, *p):
        State.__init__(self, *p)
        self.durations = list()
        
        
    def load(self, dictionary):
        State.load(self, dictionary)
        if "durations" not in dictionary:
            raise ParseException("durations were not found in GeneralizedState")
        self.durations = list(dictionary["durations"])
        for d in range(len(self.durations)):
            self.durations[d] = tuple(self.durations[d])
        
        
    def toJSON(self):
        ret = State.toJSON(self)
        ret["durations"] = self.durations
        return ret        
        
    
    def durationGenerator(self):
        return self.durations
        #for x in self.durations:
        #    yield(x)


    def emission(self, X, x, dx):
        return self.emissions[X[x:x+dx]]
    
    
    
class GeneralizedHMM(HMM):
    
        
    #Init -- je riadok 0
    def getForwardTable(self, X, x, dx, memoryPattern=None, initialRow=None):
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx + 1)
        #TODO: pridaj jednu vrstvu dictov, aby to fungovalo (lebo inac
        #pri initi stave/silent stavoch pises do dictu cez ktory sa iteruje
        #a zaroven to chces aj pouzit
        #pri odovzdavani by sa to mozno ale patrilo spojit
        # v skutocnomsti to nebude treba. Idealny stav je, ze vyrobime specialny 
        # init stav, ktory pojde do ostatnych stavov
        rows = [[defaultdict(self.mathType) 
                 for _ in range(len(self.states))] 
                     for _ in range(dx + 1)]
        
        #zacinam v 0 riadku
        ignoreFirstRow = False
        if initialRow != None:
            rows[0] = initialRow
            ignoreFirstRow = True
        else:
            for state in self.states:
                prob = state.getStartProbability()
                if prob > self.mathType(0.0):
                    rows[0][state.getStateID()][1] = prob
        
        
        # Main algorithm
        retTable = list()
        for _x in range(dx + 1):
            if ignoreFirstRow and _x == 0:
                continue
            for stateID in range(len(self.states)):
                acc_prob = reduce(operator.add, 
                                  [value for (_,value) in
                                      rows[_x][stateID].iteritems()], 
                                  self.mathType(0.0))
                state = self.states[stateID]
                for (followingID, transprob) in state.followingIDs():
                    following = self.states[followingID]
                    acc_trans_prob = acc_prob * transprob
                    for (_sdx, dprob) in following.durationGenerator():
                        if _x + _sdx > dx: 
                            continue
                        rows[_x + _sdx][followingID][_sdx] += \
                            following.emission(X, x + _x, _sdx) \
                            * acc_trans_prob * dprob
            if _x < 0:
                continue
            if memoryPattern.next():
                retTable.append((x + _x, rows[_x]))
            rows[_x] = list()
                
        return retTable
   
    
    def getBackwardTable(self, X, x, dx, memoryPattern=None, initialRow=None):
        
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx + 1)
         
        rows = [[defaultdict(self.mathType) 
                 for _ in range(len(self.states))] 
                     for _ in range(dx+1)]    
        
        ignoreFirstRow = False
        if initialRow != None:
            rows[dx] = initialRow
            ignoreFirstRow = True
        else:
            for state in self.states:
                prob = state.getEndProbability()
                if prob > self.mathType(0.0):
                    rows[dx][state.getStateID()][1] = prob
        
        # Main algorithm
        retTable = list()
        for _x in reversed(list(range(dx + 1))):
            if ignoreFirstRow and _x == dx:
                continue
            for stateID in range(len(self.states)):
                acc_prob = reduce(operator.add,
                                  [value for (_,value) in
                                      rows[_x][stateID].iteritems()],
                                  self.mathType(0.0))
                state = self.states[stateID]
                for (previousID, transprob) in state.previousIDs():
                    previous = self.states[previousID]
                    acc_trans_prob = acc_prob * transprob
                    for (_sdx, dprob) in previous.durationGenerator():
                        if _x-_sdx < 0:
                            continue
                        rows[_x - _sdx][previousID][_sdx] += \
                            state.emission(X, x + _x - _sdx, _sdx) \
                            * acc_trans_prob * dprob
            if _x>dx:
                continue 
            if memoryPattern.next():
                retTable.append((x + _x, rows[_x]))
            rows[_x] = list()
                
        return retTable
    
    
    # TODO: check if this even works
    def getProbability(self, X, x, dx, positionGenerator = None): 
        table = self.getForwardTable(X, x, dx, 
                                     memoryPattern=MemoryPatterns.last(dx + 1))
    
        return sum([sum([prob for (_, prob) in dct.iteritems()]) * self.states[stateID].getEndProbability() \
                    for (stateID, dct) in ((l, table[0][1][l]) for l in range(len(table[0][1])))])
    