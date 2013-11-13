from algorithm import MemoryPatterns
from collections import defaultdict
from hmm.HMM import State, HMM
from tools.Exceptions import ParseException
import operator
from tools.my_rand import rand_generator
from tools.structtools import recursiveArgMax, structToStr

    
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
    
   
    def buildSampleEmission(self):
        duration_dict = defaultdict(float)
        for (k, v) in self.durations:
            duration_dict[k] += v
        em = dict(self.emissions)
        for (key, _) in em.iteritems():
            em[key] *= duration_dict[len(key)]
        self._sampleEmission = rand_generator(em)
        
    
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
                        if x + _x + _sdx > len(X):
                            continue
                        rows[_x + _sdx][followingID][_sdx] += \
                            following.emission(X, x + _x, _sdx) \
                            * acc_trans_prob * dprob
            if _x < 0:
                continue
            if memoryPattern.next():
                retTable.append((_x, rows[_x]))
            rows[_x] = list()
                
        return retTable
    
    def getViterbiTable(self, X, x, dx, memoryPattern=None, initialRow=None):
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx + 1)
        #TODO: pridaj jednu vrstvu dictov, aby to fungovalo (lebo inac
        #pri initi stave/silent stavoch pises do dictu cez ktory sa iteruje
        #a zaroven to chces aj pouzit
        #pri odovzdavani by sa to mozno ale patrilo spojit
        # v skutocnomsti to nebude treba. Idealny stav je, ze vyrobime specialny 
        # init stav, ktory pojde do ostatnych stavov
            rows = [[defaultdict(lambda *x: (self.mathType(0.0), -1)) 
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
                    rows[0][state.getStateID()][0] = (prob, -1)

        # Main algorithm
        retTable = list()
        for _x in range(dx + 1):
            if ignoreFirstRow and _x == 0:
                continue
            for stateID in range(len(self.states)):
                acc_prob = reduce(max, 
                                  [value[0] for (_,value) in
                                      rows[_x][stateID].iteritems()], 
                                  self.mathType(0.0))
                state = self.states[stateID]
                for (followingID, transprob) in state.followingIDs():
                    following = self.states[followingID]
                    acc_trans_prob = acc_prob * transprob
                    for (_sdx, dprob) in following.durationGenerator():
                        if _x + _sdx > dx: 
                            continue
                        rows[_x + _sdx][followingID][_sdx] = max (
                            rows[_x + _sdx][followingID][_sdx],
                            (                                      
                                following.emission(X, x + _x, _sdx) \
                                    * acc_trans_prob * dprob,
                                stateID,
                            ),
                            key = lambda x: x[0],
                        )
                                        
            if _x < 0:
                continue
            if memoryPattern.next():
                retTable.append((_x, rows[_x]))
            rows[_x] = list()
                
        return retTable
    
    def getViterbiPath(self, table):
        #table[x][y][state][(sdx,sdy)] = (prob, previousStateId)
        _x = len(table) - 1
        ((stateID, _sdx)), (prob, previousStateId) = \
            recursiveArgMax(
                table[_x],
                selector=lambda x, y: max(x, y, key=lambda z: z[0]  )
            )
        path = [(stateID, _x, _sdx, prob)]
        stateID = previousStateId
        while stateID >= 0:
            _x -= _sdx
            _sdx, (prob, previousStateId) = max(
                table[_x][previousStateId].iteritems(),
                key=lambda (_, (prob, __)): prob
            )
            path.append((stateID, _x, _sdx, prob))
            stateID = previousStateId 
        path.reverse()
        return path
   
    
    def getBackwardTable(self, X, x, dx, memoryPattern=None, initialRow=None):
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx + 1)
         
        rows = [[self.mathType(0.0) 
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
                    rows[dx][state.getStateID()] = prob
        
        # Main algorithm
        retTable = list()
        for _x in reversed(list(range(dx + 1))):
            if ignoreFirstRow and _x == dx:
                continue
            for stateID in range(len(self.states)):
                state = self.states[stateID]
                for (previousID, transprob) in state.previousIDs():
                    previous = self.states[previousID]
                    acc_trans_prob = rows[_x][stateID] * transprob
                    for (_sdx, dprob) in previous.durationGenerator():
                        if _x-_sdx < 0:
                            continue
                        rows[_x - _sdx][previousID] += \
                            previous.emission(X, x + _x - _sdx, _sdx) \
                            * acc_trans_prob * dprob
            if _x>dx:
                continue 
            if memoryPattern.next():
                retTable.append((_x, rows[_x]))
            rows[_x] = list()
                
        return retTable
    
    def getBaumWelchCount(self, X, x, dx, memoryPattern=None, initialRow=None):
        transitions = [defaultdict(self.mathType)
                       for _ in range(len(self.states))]
        emissions = [defaultdict(self.mathType)
                     for _ in range(len(self.states))]
        forwardTable = self.getForwardTable(X, x, dx, memoryPattern, initialRow)
        ft = [[] for _ in range(len(forwardTable))]
        for i, t in forwardTable:
            ft[i] = t
        backwardTable = self.getBackwardTable(X, x, dx, memoryPattern,
                                              initialRow)
        bt = [[] for _ in range(len(backwardTable))]
        for i, t in backwardTable:
            bt[i] = t
        probability = self.getProbability(X, x, dx, table=[forwardTable[dx]])

        for i in range(dx + 1):
            for stateID in range(len(self.states)):
                state = self.states[stateID]
                for followingID, transprob in state.followingIDs():
                    for sdx, prob in ft[i][stateID].iteritems():
                        transitions[stateID][followingID] += (
                            prob * transprob * bt[i][followingID])
                        emissions[stateID][self.states[stateID].getEmissionText(
                            X,
                            x + i - sdx,
                            sdx
                        )] += (
                            prob * transprob * bt[i][followingID]
                        )
            
        return transitions, emissions, probability

    def getProbability(self, X, x, dx, positionGenerator=None, table=None):
        if table == None: 
            table = self.getForwardTable(
                X, x, dx, memoryPattern=MemoryPatterns.last(dx + 1))
    
        return sum([self.mathType(sum([prob for (_, prob) in dct.iteritems()])) 
                    * self.states[stateID].getEndProbability() 
                    for (stateID, dct) in ((l, table[0][1][l]) 
                    for l in range(len(table[0][1])))])

    def getProbabilities(self, X, x, dx, positionGenerator=None, table=None):
        if table == None:
            table = self.getForwardTable(
                X, x, dx, memoryPattern=MemoryPatterns.every(dx + 1))
        
        return [
            sum([self.mathType(sum([prob for (_, prob) in dct.iteritems()])) 
                    * self.states[stateID].getEndProbability() 
                    for (stateID, dct) in ((l, row[1][l]) 
                    for l in range(len(row[1])))])
            for row in table
        ]
