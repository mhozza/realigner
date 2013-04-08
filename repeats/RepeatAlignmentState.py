from hmm.HMM import State
from hmm import SpecialHMMs
from collections import defaultdict
from tools.my_rand import rand_generator, normalize_dict, default_dist, \
                            dist_to_json
from tools.Exceptions import ParseException
from adapters.TRFDriver import Repeat

class RepeatProfileFactory:
            
    def __init__(self, mathType=float, version='v1', repProb = None):
        self.a = 2
        self.cache = dict()
        self.mathType = mathType
        self.repProb = repProb
        self.backgroudProbability = \
            [("A", 0.25), ("C", 0.25), ("G", 0.25), ("T", 0.25)]
        self.time = 23.0
        self.transitionMatrix = {
            "MM": 0.92, "MI": 0.04, "MD": 0.04,
            "IM": 0.1, "II": 0.85, "ID": 0.05,
            "DM": 0.1, "DI": 0.1, "DD": 0.8,
            "_M": 0.8, "_I": 0.1, "_D": 0.1,
        }
        if version == 'v1':
            self.factory = SpecialHMMs.createProfileHMMv1 
        elif version == 'v2':
            self.factory = SpecialHMMs.createProfileHMMv2
        else:
            raise "Unknown version"
      
        
    def getHMM(self, consensus):
        if consensus in self.cache:
            return self.cache[consensus]
        if '_E' not in self.transitionMatrix:
            self.transitionMatrix['_E'] = self.repProb
        self.cache[consensus] = self.factory(self.mathType, 
            consensus, self.time, self.backgroudProbability,
            self.transitionMatrix)
        return self.cache[consensus]
    

class PairRepeatState(State):
    
    def __init__(self, *p):
        State.__init__(self, *p)
        self.hmm = None
        self.factory = None
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
        self.repProb = None
        self.modelversion = None
        self.trackEmissions = None
        
    
    def addRepeatGenerator(self, repeatGeneratorX, repeatGeneratorY):
        self.repeatGeneratorX = repeatGeneratorX
        self.repeatGeneratorY = repeatGeneratorY

        
    def load(self, dictionary):
        State.load(self, dictionary)
        if 'backgroundprob' not in dictionary:
            raise ParseException("Backround probability was not found in state")
        self.backgroundProbability = [tuple(x) 
                                      for x in dictionary['backgroundprob']]
        if 'time' not in dictionary:
            raise ParseException('Time was not found in state')
        self.time = dictionary['time']
        if 'transitionmatrix' not in dictionary:
            raise ParseException('Transition matrix not found in state')
        self.transitionMatrix = dictionary['transitionmatrix']
        if 'consensusdistribution' in dictionary:
            self.consensusDistribution = default_dist(normalize_dict(
                dictionary['consensusdistribution'],
                mathType=self.mathType
            ))
        if 'repeatlengthdistribution' in dictionary:
            tp = type(dictionary['repeatlengthdistribution'])
            if tp == dict:
                self.repeatLengthDistribution = \
                    default_dist(normalize_dict(
                        dictionary['repeatlengthdistribution'],
                        mathType=self.mathType
                    ))
            else:
                self.repeatLengthDistribution = \
                    dictionary['repeatlengthdistribution']
                self.repProb = self.repeatLengthDistribution.p
        if 'trackemissions' in dictionary:
            self.trackEmissions = dictionary['trackemissions']
        if 'version' in dictionary:
            self.version = dictionary['version']
        else:
            self.version = 'v1'
        if 'repprob' in dictionary:
            self.repProb = self.mathType(dictionary['repprob'])
        if self.version == 'v2':
            self.trackEmissions = defaultdict(lambda *_: self.mathType(1.0))
            self.trackEmissions['MM'] = self.mathType(1.0)
            self.repeatLengthDistribution = defaultdict(lambda *_: 
                                                        self.mathType(1.0))
            self.repeatLengthDistribution[10] = self.mathType(1.0)
        self.factory = RepeatProfileFactory(self.mathType, self.version,
                                            self.repProb)
        self.factory.backgroudProbability = self.backgroundProbability
        self.factory.time = self.time
        self.factory.transitionMatrix = self.transitionMatrix


    def toJSON(self):
        ret = State.toJSON(self)
        ret['backgroundprob'] = self.backgroundProbability
        ret['time'] = self.time
        ret['transitionmatrix'] = self.transitionMatrix
        ret['consensusdistribution'] = \
            dist_to_json(self.consensusDistribution)
        ret['repeatlengthdistribution'] = \
            dist_to_json(self.repeatLengthDistribution)
        ret['trackemissions'] = self.trackEmissions
        ret['version'] = self.version
        ret['repprob'] = self.repProb 
        #TODO: save consensus distribution
        return ret


    def durationGenerator(self, _x, _y):
        key = (_x, _y)
        if key in self.dgmemoize:
            return self.dgmemoize[key]
        X = list(self.repeatGeneratorX.getHints(_x))
        Y = list(self.repeatGeneratorY.getHints(_y))
        val = list(self.__durationGenerator(X, Y))
        self.dgmemoize[key] = val
        return val


    def reverseDurationGenerator(self, _x, _y):
        key = (_x, _y)
        if key in self.rdgmemoize:
            return self.rdgmemoize[key]
        X = list(self.repeatGeneratorX.getReverseHints(_x))
        Y = list(self.repeatGeneratorY.getReverseHints(_y))
        val = list(self.__durationGenerator(X, Y))
        self.rdgmemoize[key] = val
        return val


    def __durationGenerator(self, X, Y):
        # TODO: fix distribution
        for xlen, xcon in X:
            xrc = float(xlen) / len(xcon)
            xp = (self.repeatLengthDistribution[xrc] * 
                  self.consensusDistribution[xcon] *
                  self.trackEmissions['RM'])
            self.consensus = xcon
            yield (xlen, 0), xp
        for ylen, ycon in Y:
            yrc = float(ylen) / len(ycon)
            yp = (self.repeatLengthDistribution[yrc] * 
                  self.consensusDistribution[ycon] *
                  self.trackEmissions['MR'])
            self.consensus = ycon
            yield (0, ylen), yp
        for (xlen, xcon) in X:
            xrc = float(xlen) / len(xcon)
            xp = (self.repeatLengthDistribution[xrc] * 
                  self.consensusDistribution[xcon] *
                  self.trackEmissions['RR'])
            yp = (self.repeatLengthDistribution[xrc] *
                  self.trackEmissions['RR'])
            for (ylen, ycon) in Y:
                yrc = float(ylen) / len(ycon)
                xp *= self.repeatLengthDistribution[yrc]
                yp *= self.repeatLengthDistribution[yrc] * \
                    self.consensusDistribution[ycon]
                self.consensus = xcon
                yield((xlen, ylen), xp)
                self.consensus = ycon
                yield((xlen, ylen), yp)


    def emission(self, X, x, dx, Y, y, dy):
        # we expect that we have consensus from last generated duration 
        # TODO: fix distribution
        keyX = (self.consensus, x, dx)
        keyY = (self.consensus, y, dy)
        hmm = None
        if keyX in self.memoizeX:
            valX = self.memoizeX[keyX]
        else:
            hmm = self.factory.getHMM(self.consensus)
            if dx > 0:
                valX = hmm.getProbability(X, x, dx)
            else:
                valX = self.mathType(1.0)
            self.memoizeX[keyX] = valX
        if keyY in self.memoizeY:
            valY = self.memoizeY[keyY]
        else:
            if hmm == None:
                hmm = self.factory.getHMM(self.consensus)
            if dy > 0:
                valY = hmm.getProbability(Y, y, dy)
            else:
                valY = self.mathType(1.0)
            self.memoizeY[keyY] = valY
        return valX * valY


    def buildSampleEmission(self):
        dur = defaultdict(int)
        cons = defaultdict(int)
        total = 0;
        for rg in [self.repeatGeneratorX, self.repeatGeneratorY]:
            if rg != None:
                for rep in rg.repeats:
                    dur[rep.end - rep.start] += 1
                    cons[rep.consensus] += 1
                    total += 1
        total = float(total)
        for (key, val) in dur.iteritems():
            dur[key] = float(val) / total
        for (key, val) in cons.iteritems():
            cons[key] = float(val) / total
        if self.repeatLengthDistribution != None and self.version != 'v2':
            dur = self.repeatLengthDistribution
        if self.consensusDistribution != None:
            cons = self.consensusDistribution
        self.durationSampler = rand_generator(dur)
        self.consensusSampler = rand_generator(cons)
        self.trackEmissionsSampler = rand_generator(self.trackEmissions)
   
    
    def sampleEmission(self):
        # generate durations
        consensus = self.consensusSampler()
        
        if self.version == 'v2':
            cl = dx = dy = tuple([None])
            model_length = True
        else:
            cl = len(consensus)
            dx = int(self.durationSampler() * cl)
            dy = int(self.durationSampler() * cl)
            model_length = False
        hmm = self.factory.getHMM(consensus)
        hmm.buildSampleTransitions()
        # generate sequences
        X = hmm.generateSequence(dx, model_length) 
        Y = hmm.generateSequence(dy, model_length)
        tracks = self.trackEmissionsSampler()
        if tracks == 'MR':
            X = []
        if tracks == 'RM':
            Y = []
        X = "".join([x for (x, _) in X])
        Y = "".join([x for (x, _) in Y])
        if model_length:
            dx = len(X)
            dy = len(Y)
        # Generate Alignment
        return X, Y, (consensus, dx, dy)
    
