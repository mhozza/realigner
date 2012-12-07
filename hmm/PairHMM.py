from algorithm import MemoryPatterns
from collections import defaultdict
from hmm.GeneralizedHMM import GeneralizedState
from hmm.HMM import HMM
import operator
from tools import structtools
#from tools import visualize

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
    
    
    def durationGenerator(self, _, __):
        return GeneralizedState.durationGenerator(self)
    

    def reverseDurationGenerator(self, _, __):
        return GeneralizedState.durationGenerator(self)
    
        
    def emission(self, X, x, dx, Y, y, dy):
        return self.emissions[(X[x : x + dx], Y[y : y + dy])]
        

class GeneralizedPairHMM(HMM):
    
    def setAnnotations(self):
        return
   
    
    # Returns forward table. We can specify memory pattern, position generator
    # and initial row. Compatible with memory preserving tricks  
    # TODO: ohranicenia nefunguju ak chcem robit podsekvencie, treba to vyriesit
    def getForwardTable(self, X, x, dx, Y, y, dy,
        memoryPattern = None, positionGenerator = None, initialRow = None):
        # Default position generator
        if positionGenerator == None:
            positionGenerator = \
                ((i,j) for i in range(dx + 1) for j in range(dy + 1))
        
        # Default memory pattern (everything)
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx + 1)
        
        # Initialize table
        rows = [defaultdict(
                lambda *_:defaultdict(
                lambda *_:defaultdict(self.mathType))) for _ in range(dx + 1)]
        
        # Initialize first row
        ignoreFirstRow = False
        if initialRow != None:
            rows[0] = initialRow
            ignoreFirstRow = True
        else:
            for state in self.states:
                rows[0][0][state.getStateID()][(0, 0)] = \
                    state.getStartProbability()
        
        # Main algorithm
        _x_prev = -1000000 
        retTable = list()
        # Position generator zaruci ze nebudem mat problem menenim 
        # dictionary za jazdy. Problem to vyraba ak sa vyraba novy stav. 
        for (_x, _y) in positionGenerator:
            if ignoreFirstRow and _x == 0: #BUG: ak ignorujem prvy riadok, pokazi sa mi zapamatavanie
                continue
            for stateID in range(len(self.states)):
                acc_prob =  reduce(operator.add, 
                                  [value for (_,value) in
                                      rows[_x][_y][stateID].iteritems()], 
                                  self.mathType(0.0))
                state = self.states[stateID]
                if acc_prob <= self.mathType(0.0):
                    continue
                for (followingID, transprob) in state.followingIDs():
                    following = self.states[followingID]
                    #print("Duration: ", followingID, _x, _y, len(list(following.durationGenerator(_x, _y))), list(following.durationGenerator(_x,_y)))
                    for ((_sdx, _sdy), dprob) in \
                            following.durationGenerator(_x, _y):
                        if _x + _sdx > dx or _y + _sdy > dy:
                            continue
                        rows[_x + _sdx][_y + _sdy][followingID][(_sdx, _sdy)] \
                            += acc_prob * transprob * dprob * \
                            following.emission(
                                X, 
                                x + _x,
                                _sdx,
                                Y, 
                                y + _y, 
                                _sdy
                            )
            # If rows were changed, remember it
            if _x_prev != _x:
                if _x_prev >= 0 and _x_prev <= dx:
                    if memoryPattern.next():
                        retTable.append((x + _x_prev, rows[_x_prev]))
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
    def getBackwardTable(self, X, x, dx, Y, y, dy,
        memoryPattern = None, positionGenerator = None, initialRow = None):
        
        # Default position generator
        if positionGenerator == None:
            positionGenerator = \
                ((i,j) for i in range(dx + 1) for j in range(dy + 1))
        # Some generators have to be reversed
        positionGenerator = list(reversed(list(positionGenerator)))
      
        # Default memory pattern (everything)
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx + 1)
        
        # Initialize table
        rows = [defaultdict(
                lambda *_:defaultdict(
                lambda *_:defaultdict(self.mathType))) for _ in range(dx + 1)]
        
        # Initialize first row
        ignoreFirstRow = False
        if initialRow != None:
            rows[dx] = initialRow
            ignoreFirstRow = True
        else:
            for state in self.states:
                rows[dx][dy][state.getStateID()] [(0, 0)] = \
                    state.getEndProbability()
        
        # Main algorithm
        _x_prev = x + dx + 100000
        retTable = list()
        states = list(reversed(range(len(self.states))))
        for (_x, _y) in positionGenerator:
            if ignoreFirstRow and _x == dx:
                continue
            for stateID in states:
                acc_prob = reduce(operator.add, 
                                  [value for (_,value) in
                                      rows[_x][_y][stateID].iteritems()], 
                                  self.mathType(0.0))
                state = self.states[stateID]
                if acc_prob <= self.mathType(0.0):
                    continue
                for (previousID, transprob) in state.previousIDs():
                    previous = self.states[previousID]
                    for ((_sdx, _sdy), dprob) in \
                            previous.reverseDurationGenerator(_x, _y):
                        if _x - _sdx < 0 or _y - _sdy < 0:
                            continue
                        rows[_x - _sdx][_y - _sdy][previousID][(_sdx, _sdy)] \
                            += acc_prob * transprob * dprob * \
                            previous.emission(
                                X,
                                x + _x - _sdx,
                                _sdx,
                                Y,
                                x + _y - _sdy,
                                _sdy
                            )
            
            # Remember last row if necessary
            if _x_prev != _x:
                if _x_prev >= 0 and _x_prev <= dx:
                    if memoryPattern.next():
                        retTable.append((x + _x_prev, rows[_x_prev]))
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
    
    
    def getPosteriorTable(self, X, x, dx, Y, y, dy, 
                          forwardTable = None, backwardTable = None,
                          positionGenerator = None):
        # Najskor chcem taku, co predpoklada ze obe tabulky su velke
        # Potom chcem taku, ktora si bude doratavat chybajuce
        # Potom pridat switch, ktory mi umozni robit optimalizacie.
        # Ale potom bude treba vediet, ci ist od predu, alebo od zadu
        
        # Fetch tables if they are not provided
        if positionGenerator != None:
            positionGenerator = list(positionGenerator)
        if forwardTable == None:
            forwardTable = self.getForwardTable(X, x, dx, Y, y, dy,
                positionGenerator=positionGenerator)
        if backwardTable == None:
            backwardTable = self.getBackwardTable(X, x, dx, Y, y, dy,
                positionGenerator=positionGenerator)
        
        #=======================================================================
        # vis = visualize.Vis2D()
        # vis.addTable(forwardTable, "o", "green", visualize.containNonzeroElement, 0.0, 0.3)
        # vis.addTable(backwardTable, "o", "blue", visualize.containNonzeroElement, 0.3, 0.0)
        # vis.addPositionGenerator(positionGenerator, "o", "red")
        # vis.show()
        #=======================================================================
        
        #=======================================================================
        # f = open("debug.txt", "a")
        # f.write("forwardTableXX\n")
        # f.write(structtools.structToStr(forwardTable, 3, ""))
        # f.close()
        # f = open("debug.txt", "a")
        # f.write("backwardTable\n")
        # f.write(structtools.structToStr(backwardTable, 3, ""))
        # f.close()
        #=======================================================================

        # Sort tables by first element (just in case)    
        sorted(forwardTable,key=lambda (x,_) : x)
        sorted(backwardTable,key=lambda (x,_) : x)
        
        # Convert forward table into list
        ft = [dict() for _ in range(dx + 1)]
        
        for (i, _x) in forwardTable:
            ft[i - x] = _x
            
        # Flatten backward table
        bt = [dict() for _ in range(dx + 1)]
        for (i, B) in backwardTable:
            for _y in B:
                for state in B[_y]:
                    # Bug -- razsej by bolo lepsie vymazat povodny zaznam a 
                    # spravit to v inej tabulke. Tak ci tak 
                    B[_y][state] = reduce(operator.add, 
                                          [value for (_,value) in
                                           B[_y][state].iteritems()], 
                                          self.mathType(0.0))
            bt[i] = B
        B = defaultdict(self.mathType)
        for (_x, _y) in positionGenerator:
            for stateID in range(len(self.states)):
                state = self.states[stateID]
                acc = self.mathType(0.0)
                for (followingID, prob) in state.followingIDs():
                    if _x == 4 and _y==24:
                        print (_x, _y, followingID, bt[_x][_y][followingID])
                    acc += prob * bt[_x][_y][followingID]
                B[(_x, _y, stateID)] = acc
        
        # Compute posterior probabilities
        retTable = [defaultdict(lambda *_:defaultdict(self.mathType))
                    for _ in range(dx + 1)]
        for _x in range(dx + 1):
            for (_y, V) in ft[_x].iteritems():
                for (state, VV) in V.iteritems():
                    for ((_sdx, _sdy), prob) in VV.iteritems():
                        retTable[_x][_y][(state, _sdx, _sdy)] = \
                            prob * B[(_x, _y, state)]
                            
        
        return retTable