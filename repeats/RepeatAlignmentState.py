#TODO: Skontroluj pre kazdy config objekt ci sa dobre serializuje naspat do JSONu. Budeme to neskor vyuzivat pri ukladani parametrov z experimentov
from hmm.HMM import State
from hmm import SpecialHMMs
from collections import defaultdict
from tools.my_rand import rand_generator, normalize_dict, default_dist, \
                            dist_to_json
from tools.Exceptions import ParseException

class RepeatProfileFactory:
            
    def __init__(self, mathType=float):
        self.a = 2
        self.cache = dict()
        self.mathType = mathType
        self.backgroudProbability = \
            [("A", 0.25), ("C", 0.25), ("G", 0.25), ("T", 0.25)]
        self.time = 23.0
        self.transitionMatrix = {
            "MM": 0.92, "MI": 0.04, "MD": 0.04,
            "IM": 0.1, "II": 0.85, "ID": 0.05,
            "DM": 0.1, "DI": 0.1, "DD": 0.8,
            "_M": 0.8, "_I": 0.1, "_D": 0.1,
        }
        
    def getHMM(self, consensus):
        if consensus in self.cache:
            return self.cache[consensus]
        self.cache[consensus] = SpecialHMMs.createProfileHMM(self.mathType, 
            consensus, self.time, 
            self.backgroudProbability, self.transitionMatrix)
        return self.cache[consensus]
    

class PairRepeatState(State):
    
    def __init__(self, *p):
        State.__init__(self, *p)
        self.hmm = None
        self.factory = RepeatProfileFactory()
        self.repeatGeneratorX = None
        self.repeatGeneratorY = None
        self.consensus = ""
        self.memoizeX = dict()
        self.memoizeY = dict()
        self.dgmemoize = dict()
        self.rdgmemoize = dict()
        self.consensusSampler = None
        self.durationSampler = None
        self.backgroundProbability = None
        self.time = None
        self.transitionMatrix = None
        self.consensusDistribution = None
        self.repeatLengthDistribution = None
        
    
    def addRepeatGenerator(self, repeatGeneratorX, repeatGeneratorY):
        self.repeatGeneratorX = repeatGeneratorX
        self.repeatGeneratorY = repeatGeneratorY

        
    def load(self, dictionary):
        State.load(self, dictionary)
        if 'backgroundprob' not in dictionary:
            raise ParseException("Backround probability was not found in state")
        self.backgroundProbability = [tuple(x) 
                                      for x in dictionary['backgroundprob']]
        self.factory.backgroudProbability = self.backgroundProbability
        if 'time' not in dictionary:
            raise ParseException('Time was not found in state')
        self.time = dictionary['time']
        self.factory.time = self.time
        if 'transitionmatrix' not in dictionary:
            raise ParseException('Transition matrix not found in state')
        self.transitionMatrix = dictionary['transitionmatrix']
        self.factory.transitionMatrix = self.transitionMatrix
        if 'consensusdistribution' in dictionary:
            self.consensusDistribution = default_dist(normalize_dict(
                dictionary['consensusdistribution'],
                mathType=self.mathType
            ))
        if 'repeatlengthdistribution' in dictionary:
            self.repeatLengthDistribution = \
                default_dist(normalize_dict(
                    dictionary['repeatlengthdistribution'],
                    mathType=self.mathType
                ))


    def toJSON(self):
        ret = State.toJSON(self)
        ret['backgroundprob'] = self.backgroundProbability
        ret['time'] = self.time
        ret['transitionmatrix'] = self.transitionMatrix
        ret['consensusdistribution'] = \
            dist_to_json(self.consensusDistribution)
        ret['repeatlengthdistribution'] = \
            dist_to_json(self.repeatLengthDistribution)
        #TODO: save consensus distribution
        return ret


    def durationGenerator(self, _x, _y):
        key = (_x, _y)
        if key in self.dgmemoize:
            return self.dgmemoize[key]
        val = list(self._durationGenerator(_x, _y))
        self.dgmemoize[key] = val
        return val


    def _durationGenerator(self, _x, _y):
        X = list(self.repeatGeneratorX.getHints(_x))
        Y = list(self.repeatGeneratorY.getHints(_y))
        for (xlen, xcon) in X:
            xp = self.repeatLengthDistribution[xlen] * \
                self.consensusDistribution[xcon]
            yp = self.repeatLengthDistribution[xlen]
            for (ylen, ycon) in Y:
                xp *= self.repeatLengthDistribution[ylen]
                yp *= self.repeatLengthDistribution[ylen] * \
                    self.consensusDistribution[ycon]
                self.consensus = xcon
                yield((xlen, ylen), xp)
                self.consensus = ycon
                yield((xlen, ylen), yp)


    def reverseDurationGenerator(self, _x, _y):
        key = (_x, _y)
        if key in self.rdgmemoize:
            return self.rdgmemoize[key]
        val = list(self._reverseDurationGenerator(_x, _y))
        self.rdgmemoize[key] = val
        return val


    def _reverseDurationGenerator(self, _x, _y):
        X = list(self.repeatGeneratorX.getReverseHints(_x))
        Y = list(self.repeatGeneratorY.getReverseHints(_y))
        for (xlen, xcon) in X:
            xp = self.repeatLengthDistribution[xlen] * \
                self.consensusDistribution[xcon]
            yp = self.repeatLengthDistribution[xlen]
            for (ylen, ycon) in Y:
                xp *= self.repeatLengthDistribution[ylen]
                yp *= self.repeatLengthDistribution[ylen] * \
                    self.consensusDistribution[ycon]
                self.consensus = xcon
                yield((xlen, ylen), xp)
                self.consensus = ycon
                yield((xlen, ylen), yp)


    def emission(self, X, x, dx, Y, y, dy):
        # we expect that we have consensus from last generated duration  
        keyX = (self.consensus, x, dx)
        keyY = (self.consensus, y, dy)
        hmm = None
        if keyX in self.memoizeX:
            valX = self.memoizeX[keyX]
        else:
            hmm = self.factory.getHMM(self.consensus)
            valX = hmm.getProbability(X, x, dx)
            self.memoizeX[keyX] = valX
        if keyY in self.memoizeY:
            valY = self.memoizeY[keyY]
        else:
            if hmm == None:
                hmm = self.factory.getHMM(self.consensus)
            valY = hmm.getProbability(Y, y, dy)
            self.memoizeY[keyY] = valY
        return valX * valY


    def buildSampleEmission(self):
        # TODO: save and load this shit from file 
        dur = defaultdict(int)
        cons = defaultdict(int)
        total = 0;
        for rg in [self.repeatGeneratorX, self.repeatGeneratorY]:
            for rep in rg.repeats:
                dur[rep.end - rep.start] += 1
                cons[rep.consensus] += 1
                total += 1
        total = float(total)
        for (key, val) in dur.iteritems():
            dur[key] = float(val) / total
        for (key, val) in cons.iteritems():
            cons[key] = float(val) / total
        if self.repeatLengthDistribution != None:
            dur = self.repeatLengthDistribution
        if self.consensusDistribution != None:
            cons = self.consensusDistribution
        self.durationSampler = rand_generator(dur)
        self.consensusSampler = rand_generator(cons)
        
    
    def sampleEmission(self):
        # generate durations
        dx, dy = self.durationSampler(), self.durationSampler()
        # generate consensus
        consensus = self.consensusSampler()
        print('DEBUG', consensus)
        hmm = self.factory.getHMM(consensus)
        hmm.buildSampleTransitions()
        # generate sequences
        X, Y = hmm.generateSequence(dx), hmm.generateSequence(dy)
        X = "".join([x for (x, _) in X])
        Y = "".join([x for (x, _) in Y])
        # Generate Alignment
        return X, Y