from algorithm import MemoryPatterns
from collections import defaultdict
from hmm.GeneralizedHMM import GeneralizedState
from hmm.HMM import HMM
import operator
from tools.my_rand import rand_generator
from tools.structtools import recursiveArgMax
from tools import perf
from tools.debug import jcpoint

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
    
    
    def durationGenerator(self, _=None, __=None):
        return GeneralizedState.durationGenerator(self)
    

    def reverseDurationGenerator(self, _=None, __=None):
        return GeneralizedState.durationGenerator(self)
    
        
    def emission(self, X, x, dx, Y, y, dy):
        return self.emissions[(X[x : x + dx], Y[y : y + dy])]
    
    
    def buildSampleEmission(self):
        duration_dict = defaultdict(float)
        for (k, v) in self.durations:
            duration_dict[k] += v
        em = dict(self.emissions)
        for (key, _) in em.iteritems():
            em[key] *= duration_dict[(len(key[0]), len(key[1]))]
        self._sampleEmission = rand_generator(em)
        
    def augmentSequences(self, A, B):
        return A[0][A[1]:A[1] + A[2]], B[0][B[1]:B[1] + B[2]] 
    
    def trainEmissions(self, emissions):
        total = self.mathType(sum(emissions.values()))
        self.emissions = defaultdict(self.mathType)
        for k, v in emissions.iteritems():
            self.emissions[k] = self.mathType(v) / total

    def add_soft_masking_to_distribution(self):
        d = defaultdict(lambda *_: defaultdict(list))
        for (x, y), p in self.emissions.iteritems():
            dx = len(x)
            dy = len(y)
            k = (dx, dy)
            assert(dx <= 1)
            assert(dy <= 1)
            if dx == 1 and y != 'N':
                d[k][('N', y)].append(p)
            if dy == 1 and x != 'N':
                d[k][(x, 'N')].append(p)
            if dx == 1 and dy == 1 and x != 'N' and y != 'N':
                d[k][('N', 'N')].append(p)
        for kk, v in d.iteritems():
            for k, l in v.iteritems(): 
                if len(l) == 0:
                    continue
                self.emissions[k] = self.mathType(sum(l) / len(l))


class PosteriorTableProcessor:
    
    def __init__(self, dx, model):
        self.retTable = [defaultdict(lambda *_:defaultdict(model.mathType))
                    for _ in range(dx + 1)]
        self.model = model

    def processRow(self, X, x, dx, Y, y, dy, i, row, bt, positionGenerator):
        B = defaultdict(self.model.mathType)
        for (_x, _y) in positionGenerator:
            for stateID in range(len(self.model.states)):
                state = self.model.states[stateID]
                acc = sum([prob * bt[_x][_y][followingID]
                           for (followingID, prob) in state.followingIDs()])
                B[(_y, stateID)] = acc    
        for (_y, V) in row.iteritems():
            for state in range(len(V)):
                for ((_sdx, _sdy), prob) in V[state].iteritems():
                    self.retTable[i][_y][(state, _sdx, _sdy)] = \
                        prob * B[(_y, state)]
        del B

    def getData(self):
        return self.retTable
    
    
class BaumWelchProcessor:
    
    def __init__(self, dx, model):
        self.transitionCount = defaultdict(model.mathType)
        self.emissionCount = [defaultdict(model.mathType) 
                              for _ in range(len(model.states))]
        self.model = model
    
    def processRow(self, X, x, dx, Y, y, dy, i, row, bt, positionGenerator):
        F = defaultdict(self.model.mathType)
        for _y, V in row.iteritems():
            for state in range(len(V)):
                for ((_sdx, _sdy), prob) in V[state].iteritems():
                    F[_y, state] += prob
        
        B = defaultdict(self.model.mathType)
        for (_x, _y) in positionGenerator:
            for stateID in range(len(self.model.states)):
                state = self.model.states[stateID]
                acc = self.model.mathType(0.0)
                for (followingID, prob) in state.followingIDs():
                    acc += prob * bt[_x][_y][followingID]
                B[(_y, stateID)] = acc
        
        for _x, _y in positionGenerator:
            for stateID in range(len(self.model.states)):
                state = self.model.states[stateID]
                for followingID, prob in state.followingIDs():
                    self.transitionCount[stateID, followingID] += (
                        F[_y, stateID] * prob * bt[_x][_y][followingID])
        del F
        
        for (_y, V) in row.iteritems():
            for state in range(len(V)):
                for ((_sdx, _sdy), prob) in V[state].iteritems():
                    if _sdx == 0 and _sdy == 0:
                        continue #TODO: find out why this happens
                    self.emissionCount[state][# spadne na unhashable
                        self.model.states[state].augmentSequences(
                            (X, x + i - _sdx, _sdx),
                            (Y, y + _y - _sdy, _sdy),
                        )
                    ] += prob * B[(_y, state)]
        del B
    
    def getData(self):
        return self.transitionCount, self.emissionCount

   
class ProbabilityProcessor:

    def __init__(self, dx, model):
        self.ret = model.mathType(0.0)
        pass

    def processRow(self, X, x, dx, Y, y, dy, i, row, bt, positionGenerator):
        if i != dx:
            return;
        for V in row[dy]:
            for _, prob in V.iteritems():
                self.ret += prob

    def getData(self):
        return self.ret


class GeneralizedPairHMM(HMM):
    
    def setAnnotations(self):
        return
   
    
    # Returns forward table. We can specify memory pattern, position generator
    # and initial row. Compatible with memory preserving tricks  
    # TODO: ohranicenia nefunguju ak chcem robit podsekvencie, treba to vyriesit
    def getForwardTable(self, X, x, dx, Y, y, dy,
                        memoryPattern=None, positionGenerator=None, initialRow=None):
        # Default position generator
        if positionGenerator == None:
            positionGenerator = \
                ((i, j) for i in range(dx + 1) for j in range(dy + 1))

        # Default memory pattern (everything)
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx + 1)

        # Initialize table
        rows = [defaultdict(
                lambda *_: [defaultdict(self.mathType)
                            for _ in range(len(self.states))]) 
                for _ in range(dx + 1)]

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
            if ignoreFirstRow and _x == 0: #FIXME: ak ignorujem prvy riadok, pokazi sa mi zapamatavanie
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

        return retTable

    def getForwardTableGenerator(self, X, x, dx, Y, y, dy,
                                 memoryPattern=None, positionGenerator=None, initialRow=None):
        # Default position generator
        if positionGenerator == None:
            positionGenerator = \
                ((i, j) for i in range(dx + 1) for j in range(dy + 1))

        # Default memory pattern (everything)
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx + 1)

        # Initialize table
        rows = [defaultdict(
            lambda *_: [defaultdict(self.mathType)
                        for _ in range(len(self.states))])
                for _ in range(dx + 1)]

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
        # Position generator zaruci ze nebudem mat problem menenim 
        # dictionary za jazdy. Problem to vyraba ak sa vyraba novy stav.
        for (_x, _y) in positionGenerator:
            if ignoreFirstRow and _x == 0: #FIXME: ak ignorujem prvy riadok, pokazi sa mi zapamatavanie
                continue
            for stateID in range(len(self.states)):
                acc_prob = reduce(operator.add,
                                  [value for (_, value) in
                                   rows[_x][_y][stateID].iteritems()],
                                  self.mathType(0.0))
                state = self.states[stateID]
                if acc_prob <= self.mathType(0.0):
                    continue
                for (followingID, transprob) in state.followingIDs():
                    following = self.states[followingID]
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
                        yield x + _x_prev, rows[_x_prev]
                    rows[_x_prev] = list()
            _x_prev = _x

        # Remember last row if necessary
        if memoryPattern.next():
            yield x + _x_prev, rows[dx]


    # Basically copy of the getForwardTable. Might share bugs
    # TODO: +- 1
    # TODO: restrictions
    # TODO: reverse memory pattern?
    def getBackwardTable(self, X, x, dx, Y, y, dy,
                         memoryPattern=None, positionGenerator=None,
                         initialRow=None):

        # Default position generator
        if positionGenerator == None:
            positionGenerator = \
                ((i, j) for i in range(dx + 1) for j in range(dy + 1))
            # Some generators have to be reversed
        positionGenerator = list(reversed(list(positionGenerator)))

        # Default memory pattern (everything)
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx + 1)

        # Initialize table
        rows = [defaultdict(
                lambda *_: [self.mathType(0.0) 
                            for _ in range(len(self.states))]) 
                for _ in range(dx + 1)]

        # Initialize first row
        ignoreFirstRow = False
        if initialRow != None:
            rows[dx] = initialRow
            ignoreFirstRow = True
        else:
            for state in self.states:
                rows[dx][dy][state.getStateID()] = \
                    state.getEndProbability()

        # Main algorithm
        _x_prev = x + dx + 100000
        retTable = list()
        states = list(reversed(range(len(self.states))))
        for (_x, _y) in positionGenerator:
            if ignoreFirstRow and _x == dx:
                continue
            for stateID in states:
                acc_prob = rows[_x][_y][stateID]
                state = self.states[stateID]
                if acc_prob <= self.mathType(0.0):
                    continue
                for (previousID, transprob) in state.previousIDs():
                    previous = self.states[previousID]
                    for ((_sdx, _sdy), dprob) in \
                            previous.reverseDurationGenerator(_x, _y):
                        if _x - _sdx < 0 or _y - _sdy < 0 or _x - _sdx > dx or _y - _sdy > dy:
                            continue
                        rows[_x - _sdx][_y - _sdy][previousID] += (
                            acc_prob * transprob * dprob * 
                            previous.emission(
                                X,
                                x + _x - _sdx,
                                _sdx,
                                Y,
                                x + _y - _sdy,
                                _sdy
                            )
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


    def getViterbiTable(self, X, x, dx, Y, y, dy,
                        memoryPattern=None, positionGenerator=None,
                        initialRow=None):
        # NOTICE: toto je len skopirovane z forward Table a upravene
        # Toto by malo byt rovnake ako pred tym 
        # Default position generator
        if positionGenerator == None:
            positionGenerator = \
                ((i, j) for i in range(dx + 1) for j in range(dy + 1))

        # Default memory pattern (everything)
        if memoryPattern == None:
            memoryPattern = MemoryPatterns.every(dx + 1)

        # Initialize table
        rows = [
            defaultdict(
                lambda *_: [defaultdict(
                        lambda *_:
                        (
                            self.mathType(0.0), 
                            -1
                        )
                    ) for _ in range(len(self.states))
                ]
            )
            for _ in range(dx + 1)
        ]

        # Initialize first row
        ignoreFirstRow = False
        if initialRow != None:
            rows[0] = initialRow
            ignoreFirstRow = True
        else:
            for state in self.states:
                rows[0][0][state.getStateID()][(0, 0)] = \
                    (state.getStartProbability(), -1)

        # Main algorithm
        _x_prev = -1000000
        retTable = list()
        # Position generator zaruci ze nebudem mat problem menenim 
        # dictionary za jazdy. Problem to vyraba ak sa vyraba novy stav. 
        for (_x, _y) in positionGenerator:
            if ignoreFirstRow and _x == 0:
                continue
            for stateID in range(len(self.states)):
                acc_prob = reduce(max,
                                  [value[0] for (_, value) in
                                   rows[_x][_y][stateID].iteritems()],
                                  self.mathType(0.0))
                state = self.states[stateID]
                if acc_prob <= self.mathType(0.0):
                    continue
                for (followingID, transprob) in state.followingIDs():
                    following = self.states[followingID]
                    for ((_sdx, _sdy), dprob) in \
                            following.durationGenerator(_x, _y):
                        if _x + _sdx > dx or _y + _sdy > dy or _x + _sdx < 0 or _y + _sdy < 0:
                            continue
                        #dprob = self.mathType(1.0)
                        rows[_x + _sdx][_y + _sdy][followingID][(_sdx, _sdy)] \
                            = max(
                                  rows[_x + _sdx][_y + _sdy][followingID][(_sdx, _sdy)],
                                  (
                                      acc_prob * transprob * dprob * \
                                      following.emission(
                                                         X, 
                                                         x + _x,
                                                         _sdx,
                                                         Y, 
                                                         y + _y, 
                                                         _sdy
                                      ),
                                      stateID
                                  ),
                                  key=lambda x: x[0]                                   
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
        ret = [dict() for _ in range(dx + 1)]
        for i, _x in retTable:
            ret[i - x] = _x
        return ret


    def getViterbiPath(self, table):
        #table[x][y][state][(sdx,sdy)] = (prob, previousStateId)
        _x = len(table) - 1
        _y = max([k for k in table[-1]])
        (stateID, (_sdx, _sdy)), (prob, previousStateId) = \
            recursiveArgMax(
                table[_x][_y],
                selector=lambda x, y: max(x, y, key=lambda z, _: z)
            )

        path = [(stateID, (_x, _y), (_sdx, _sdy), prob)]
        stateID = previousStateId
        while stateID >= 0:
            _x -= _sdx
            _y -= _sdy
            (_sdx, _sdy), (prob, previousStateId) = max(
                table[_x][_y][previousStateId].iteritems(),
                key=lambda (_, (prob, __)): prob
            )
            path.append((stateID, (_x, _y), (_sdx, _sdy), prob))
            stateID = previousStateId
        path.reverse()
        return path
            

    def getProbability(self, X, Y, x, y, dx, dy, positionGenerator = None):
        table = self.getForwardTable(X, Y, x, y, dx, dy, 
                                     memoryPattern=MemoryPatterns.last(dx),
                                     positionGenerator=positionGenerator)
        r = self.getTable(X, x, dx, Y, y, dy, [self.probabilityResult], 
                          table, [], positionGenerator) #TODO tu som robil zmenu
        return r[0]



    def posteriorTableResult(self, X, x, dx, Y, y, dy, ft, bt,
                             positionGenerator):
        # Compute posterior probabilities
        B = defaultdict(self.mathType)
        for (_x, _y) in positionGenerator:
            for stateID in range(len(self.states)):
                state = self.states[stateID]
                acc = self.mathType(0.0)
                for (followingID, prob) in state.followingIDs():
                    acc += prob * bt[_x][_y][followingID]
                B[(_x, _y, stateID)] = acc

        retTable = [defaultdict(lambda *_: defaultdict(self.mathType))
                    for _ in range(dx + 1)]
        for _x in range(dx + 1):
            for (_y, V) in ft[_x].iteritems():
                for state in range(len(V)):
                    for ((_sdx, _sdy), prob) in V[state].iteritems():
                        retTable[_x][_y][(state, _sdx, _sdy)] = \
                            prob * B[(_x, _y, state)]
        return retTable


    def probabilityResult(self, X, x, dx, Y, y, dy, ft, bt,
                          positionGenerator):
        # Compute probability of sequence
        ret = self.mathType(0.0)
        for V in ft[dx][dy]:
            for _, prob in V.iteritems():
                ret += prob
        return ret


    def EmissionCountResult(self, X, x, dx, Y, y, dy, ft, bt,
                            positionGenerator):
        B = defaultdict(self.mathType)
        for (_x, _y) in positionGenerator:
            for stateID in range(len(self.states)):
                state = self.states[stateID]
                acc = self.mathType(0.0)
                for (followingID, prob) in state.followingIDs():
                    acc += prob * bt[_x][_y][followingID]
                B[(_x, _y, stateID)] = acc

        retTable = defaultdict(lambda *_: defaultdict(self.mathType))
        # retTable[state][emission] = probability
        for _x in range(dx + 1):
            for (_y, V) in ft[_x].iteritems():
                for state in range(len(V)):
                    for ((_sdx, _sdy), prob) in V[state].iteritems():
                        retTable[state][(X[x + _x - _sdx:x + _x],
                                         Y[y + _y - _sdy:y + _y])] \
                            += prob * B[(_x, _y, state)]
        return retTable


    def TransitionCountResult(self, X, x, dx, Y, y, dy, ft, bt,
                              positionGenerator):
        retTable = defaultdict(lambda *_: defaultdict(self.mathType))
        for _x in range(dx + 1):
            for (_y, V) in ft[_x].iteritems():
                for state in range(len(V)):
                    for ((_sdx, _sdy), prob) in V[state].iteritems():
                        for stateID in range(len(self.states)):
                            state = self.states[stateID]
                            for (followingID, tprob) in state.followingIDs():
                                retTable[stateID][followingID] += \
                                    bt[_x][_y][followingID] * prob * tprob
        return retTable


    def getTable(self, X, x, dx, Y, y, dy, tables,
                 forwardTable=None, backwardTable=None,
                 positionGenerator=None):
        # Najskor chcem taku, co predpoklada ze obe tabulky su velke
        # Potom chcem taku, ktora si bude doratavat chybajuce
        # Potom pridat switch, ktory mi umozni robit optimalizacie.
        # Ale potom bude treba vediet, ci ist od predu, alebo od zadu
        # Fetch tables if they are not provided
        if positionGenerator != None:
            positionGenerator = list(positionGenerator)
        perf.push()
        forwardTable = jcpoint(
            lambda:
                forwardTable 
                if forwardTable != None else
                self.getForwardTableGenerator(X, x, dx, Y, y, dy,
                    positionGenerator=positionGenerator),
            'forward_table',
            self.io_files, 
            self.mathType,
        )
        perf.msg('Forward table was computed in {time} seconds.')
        perf.replace()
        backwardTable = jcpoint(
            lambda:
                backwardTable
                if backwardTable != None else
                self.getBackwardTable(X, x, dx, Y, y, dy,
                    positionGenerator=positionGenerator),
            'backward_table',
            self.io_files,
            self.mathType,
        )
        perf.msg('Backward table was computed in {time} seconds.')
        perf.replace()
        # Sort tables by first element (just in case)    
        sorted(backwardTable,key=lambda (x,_) : x)
        perf.msg('Tables were sorted in {time} seconds.')
        perf.replace()

        # Convert forward table into list
        #ft = [dict() for _ in range(dx + 1)]

        #for (i, _x) in forwardTable:
        #    ft[i - x] = _x

        # Convert backward table into list
        bt = [dict() for _ in range(dx + 1)]
        for (i, B) in backwardTable:
            bt[i] = B
        perf.msg('Backward table was flattened in {time} seconds.')
        perf.replace()

        States = [table(dx, self) for table in tables]
        index = 0
        for i, row in forwardTable:
            #slice position generator
            while (index < len(positionGenerator) and 
                   positionGenerator[index][0] < i):
                index += 1
            start = index
            while (index < len(positionGenerator) and
                   positionGenerator[index][0] <= i):
                index += 1

            for table in States:
                table.processRow(X, x, dx, Y, y, dy, i, row, bt, 
                                 positionGenerator[start:index])
        ret = [table.getData() for table in States]

#        ret = [table(X, x, dx, Y, y, dy, ft, bt, positionGenerator) 
#                for table in tables]
        perf.msg('Posterior table was computed in {time} seconds.')
        perf.pop()
        return ret


    def getPosteriorTable(self, X, x, dx, Y, y, dy,
                          forwardTable=None, backwardTable=None,
                          positionGenerator=None):
        r = self.getTable(X, x, dx, Y, y, dy, [PosteriorTableProcessor,
                                               ProbabilityProcessor],
                          forwardTable, backwardTable, positionGenerator)
        assert(len(r) == 2)
        return tuple(r)


    def getBaumWelchCounts(self, X, x, dx, Y, y, dy,
                 forwardTable = None, backwardTable = None,
                 positionGenerator = None):
        r = self.getTable(X, x, dx, Y, y, dy, [BaumWelchProcessor,
                                               ProbabilityProcessor],
                          forwardTable, backwardTable, positionGenerator)
        assert(len(r) == 2)
        return tuple(r)
