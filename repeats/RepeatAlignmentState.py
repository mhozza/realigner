from hmm.HMM import State
from hmm import SpecialHMMs
from collections import defaultdict
from tools.my_rand import rand_generator, normalize_dict, default_dist, \
                            dist_to_json
from tools.Exceptions import ParseException
import math
#from multiprocessing import Pool

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
        if '_E' not in self.transitionMatrix: # TODO: neskor chceme iny system detekcie
            one = self.mathType(1.0)
            for k, v in self.transitionMatrix.iteritems():
                self.transitionMatrix[k] = self.mathType(v)

            self.transitionMatrix['_M'] = (self.transitionMatrix['_M'] * 
                                           (one - self.repProb))
            self.transitionMatrix['_I'] = (self.transitionMatrix['_I'] * 
                                           (one - self.repProb))
            self.transitionMatrix['_D'] = (self.transitionMatrix['_D'] * 
                                           (one - self.repProb))
            self.transitionMatrix['_E'] = self.repProb
            self.transitionMatrix['DE'] = (self.transitionMatrix['_M'] * 
                                           self.repProb)
            self.transitionMatrix['DRM'] = (self.transitionMatrix['_M'] * 
                                            (one - self.repProb))
            self.transitionMatrix['DRI'] = (self.transitionMatrix['_I'] * 
                                            (one - self.repProb))
            self.transitionMatrix['DRE'] = (self.transitionMatrix['_I'] * 
                                            self.repProb)
            self.transitionMatrix['DRD'] = (self.transitionMatrix['_D'] * 
                                            (one - self.repProb))
            self.transitionMatrix['MR_'] = ((one - self.transitionMatrix['MI']) 
                                            * (one - self.repProb))
            self.transitionMatrix['MRE'] = ((one - self.transitionMatrix['MI']) 
                                            * self.repProb)
            self.transitionMatrix['IR_'] = ((one - self.transitionMatrix['II']) 
                                            * (one - self.repProb))
            self.transitionMatrix['IRE'] = ((one - self.transitionMatrix['II'])
                                            * self.repProb)
            self.transitionMatrix['MRI'] = self.transitionMatrix['MI']
            self.transitionMatrix['IRI'] = self.transitionMatrix['II']
            self.transitionMatrix['_E'] = self.repProb
        self.cache[consensus] = self.factory(self.mathType, 
            consensus, self.time, self.backgroudProbability,
            self.transitionMatrix)
        return self.cache[consensus]
    
    def clearCache(self):
        self.cache = dict()
    

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
        if self.version != None:
            ret['version'] = self.version
        if self.repProb != None:
            ret['repprob'] = float(self.repProb) 
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
    
    
    def getCons(self, x, dx, y, dy):
        ret = []
        if dx > 0:
            for ln, consensus in self.repeatGeneratorX.getHints(x):
                if ln == dx:
                    ret.append(consensus)
        if dy > 0:
            for ln, consensus in self.repeatGeneratorY.getHints(y):
                if ln == dy:
                    ret.append(consensus)
        return ret
            
    
    def augmentSequences(self, A, B):
        # Expecting that these values are cached. If not, it will not work
        X, x, dx = A
        Y, y, dy = B
        ret = defaultdict(self.mathType)
        for consensus in self.getCons(x, dx, y, dy):
            keyX = (consensus, x, dx)
            keyY = (consensus, y, dy)
            prob = self.mathType(1.0)
            if keyX in self.memoizeX:
                prob *= self.memoizeX[keyX]
            if keyY in self.memoizeY:
                prob *= self.memoizeY[keyY]
            ret[consensus] += prob 
        #print X[x:x + dx], Y[y:y + dy], tuple(ret.iteritems())
        return X[x:x + dx], Y[y:y + dy], tuple(ret.iteritems())
    
    def clearCache(self):
        self.memoizeX = dict()
        self.memoizeY = dict()
        self.dgmemoize = dict()
        self.rdgmemoize = dict()
        self.factory.clearCache()
    
    def combineExpectations(self, expectations):
        def name_to_type(name):
            d = {'Init': '_', 'End': 'E'}
            d1 = {'m': 'M', 'i': 'I'}
            d2 = {'1d': 'D', '2d': 'D'} 
            if name in d:
                return d[name], -1
            if name[0] in d1:
                return d1[name[0]], int(name[1:])
            if name[:2] in d2:
                return d2[name[:2]], int(name[2:])
            raise 'Unknown state name'
        
        def emission_to_realemission(state, emission, char):
            return 1 if char == emission else 0
        # TODO: zmen na dicty
        transitions = defaultdict(self.mathType)
        emissions = defaultdict(lambda *_:defaultdict(self.mathType))
        like = self.mathType(0.0)
        #pool = Pool(processes=2)
        #def __transform(arg):
        #    (x, y, consensus), prob = arg
        #    hmm = self.factory.getHMM(consensus)
        #    out = []
        #    for seq in [x, y]:
        #        if len(seq) == 0:
        #            continue
        #        out.append(hmm.getBaumWelchCount(seq, 0, len(seq)))
        #    return consensus, prob, hmm, out
        # Parallel implementation. In reality is slower:-/  
        #for consensus, prob, hmm, out in pool.map(__transform ,list(expectations.iteritems())):
        #    clen = len(consensus)
        #    for trans, emiss, likelihood in out:
        for (x, y, consensus), prob in list(expectations.iteritems()):
            clen = len(consensus)
            hmm = self.factory.getHMM(consensus)
            for sequence in [x, y]:
                if len(sequence) == 0:
                    continue
                trans, emiss, likelihood = hmm.getBaumWelchCount(sequence, 0, len(sequence))
                # TODO: Netreba tie veci nahodou uz normalizovat tu? alebo vydelit expectations likelihoodom? 
                like += likelihood * prob
                for fi in range(len(hmm.states)):
                    fname = hmm.states[fi].stateName
                    fn, findex = name_to_type(fname)
                    #Transitions for state fi
                    for ti, p in trans[fi].iteritems():
                        tname = hmm.states[ti].stateName
                        tn, _ = name_to_type(tname)
                        if ((fn == 'I' and findex == clen) or 
                            (fn in ['M', 'D'] and findex == clen - 1)):
                            transitions[fn + 'R' + tn] += prob * p
                        else:
                            transitions[fn + tn] += prob * p
                    #Emissions for state fi
                    for em, p in emiss[fi].iteritems():
                        if len(em) == 0: 
                            continue
                        if fn == 'M':
                            em = emission_to_realemission(fn, em, 
                                                          consensus[findex])
                        emissions[fn][em] += prob * p
        return transitions, emissions, like
    
    def improveModel(self, transitions, emissions):  
        self.clearCache()
        back = list(normalize_dict(emissions['I'], self.mathType).iteritems())
        self.backgroundProbability = back
        self.factory.backgroudProbability = back
        eqprob = emissions['M'][1] / sum(emissions['M'].values())
        time = -3.0/4.0 * (math.log((self.mathType(4.0) * eqprob - 1.0)/3.0))
        self.time = time
        self.factory.time = time
        totals = defaultdict(self.mathType)
        for k, v in transitions.iteritems():
            totals[k[:-1]] += v
        for state in transitions:
            transitions[state] /= totals[state[:-1]]
        self.transitionMatrix = transitions
        self.factory.transitionMatrix = transitions
         
    
    def trainEmissions(self, expect):
        lastLike = self.mathType(0.0)
        
        transitions, emissions, like = self.combineExpectations(expect)
        print 'Likelihood', like, like.value
        iterations = 0
        def diff(like, lastLike):
            if type(like) == float:
                if like >= lastLike:
                    return like - lastLike
                print 'Warning: last likelihood was smaller then previous', like.value, lastLike.value
                return lastLike - like
            else:
                if like >= lastLike:
                    return like.value - lastLike.value
                print 'Warning: last likelihood was smaller then previous', like.value, lastLike.value
                return lastLike.value - like.value
        while diff(like, lastLike) > 1e-6:
            print 'New Iteration'
            lastLike = self.mathType(like)
            self.improveModel(transitions, emissions)
            transitions, emissions, like = self.combineExpectations(expect)
            print 'Likelihood', like, like.value
            iterations += 1
            if iterations > 5:
                break
        self.improveModel(transitions, emissions)