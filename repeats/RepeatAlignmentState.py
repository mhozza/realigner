from hmm.HMM import State
from hmm import SpecialHMMs
from collections import defaultdict
from tools.my_rand import rand_generator, normalize_dict, default_dist, \
                            dist_to_json
from tools.Exceptions import ParseException
import math
from multiprocessing import Pool
from random import shuffle

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
        self.memoizeX = defaultdict(dict)
        self.memoizeY = defaultdict(dict)
        self.memoizeXsimple = dict()
        self.memoizeYsimple = dict()
        self.merge_consensus = False
        self.correctly_merge_consensus = False
        #self.dgmemoize = dict()
        #self.rdgmemoize = dict()
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
        self.x_count = 0
        self.y_count = 0
        self.cons_set = set()
        self.cons_list = list()
        
    
    def addRepeatGenerator(self, repeatGeneratorX, repeatGeneratorY):
        self.repeatGeneratorX = repeatGeneratorX
        self.repeatGeneratorY = repeatGeneratorY
        self.cons_set = self.repeatGeneratorX.cons | self.repeatGeneratorY.cons
        self.cons_list = list(self.cons_set)

        
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
        else:
            self.consensusDistribution = defaultdict(lambda *x: self.mathType(1.0))
        if 'repeatlengthdistribution' in dictionary:
            tp = type(dictionary['repeatlengthdistribution'])
            if tp in [dict, defaultdict]:
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
        if self.consensusDistribution != None:
            ret['consensusdistribution'] = \
                dist_to_json(self.consensusDistribution)
        if self.repeatLengthDistribution != None:
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
        #key = (_x, _y)
        #if key in self.dgmemoize:
        #    return self.dgmemoize[key]
        X = list(set(self.repeatGeneratorX.getHints(_x)))
        Y = list(set(self.repeatGeneratorY.getHints(_y)))
        val = list(self.__durationGenerator(X, Y))
        #self.dgmemoize[key] = val
        return val


    def reverseDurationGenerator(self, _x, _y):
        #key = (_x, _y)
        #if key in self.rdgmemoize:
        #    return self.rdgmemoize[key]
        X = list(set(self.repeatGeneratorX.getReverseHints(_x)))
        Y = list(set(self.repeatGeneratorY.getReverseHints(_y)))
        val = list(self.__durationGenerator(X, Y))
        #self.rdgmemoize[key] = val
        return val


    def __durationGenerator(self, X, Y):
        # TODO: fix distribution
        # TODO: distribution might be bad...
        for con in self.cons_list:
            for xlen in X:
                xrc = float(xlen) / len(con)
                xp = (self.repeatLengthDistribution[xrc] * 
                      self.consensusDistribution[con] *
                      self.trackEmissions['RM'])
                self.consensus = con
                yield (xlen, 0), xp
            for ylen in Y:
                yrc = float(ylen) / len(con)
                yp = (self.repeatLengthDistribution[yrc] * 
                      self.consensusDistribution[con] *
                      self.trackEmissions['MR'])
                self.consensus = con
                yield (0, ylen), yp
            for xlen in X:
                xrc = float(xlen) / len(con)
                xp = (self.repeatLengthDistribution[xrc] * 
                      self.consensusDistribution[con] *
                      self.trackEmissions['RR'])
                for ylen in Y:
                    yrc = float(ylen) / len(con)
                    xp *= self.repeatLengthDistribution[yrc]
                    self.consensus = con
                    yield((xlen, ylen), xp)
            if self.merge_consensus or self.correctly_merge_consensus:
                break

    def getHMM(self, consensus):
        return self.factory.getHMM(consensus)

    def emissionX(self, X, x, dx, cons=None):
        if self.merge_consensus or self.correctly_merge_consensus:
            keyX = (x, dx)
            if keyX in self.memoizeXsimple:
                return self.memoizeXsimple[keyX]
            cons_list = self.cons_list
            if cons != None:
                cons_list = cons
            first = True
            fun = lambda x:x
            if self.correctly_merge_consensus:
                fun = lambda x:[x]
            for consensus in cons_list:
                hmm = self.factory.getHMM(consensus)
                valX = hmm.getProbabilities(X, x, dx)
                for ddx in range(dx + 1):
                    if first:
                        self.memoizeXsimple[(x, ddx)] = fun(valX[ddx])
                    else:
                        self.memoizeXsimple[(x, ddx)] += fun(valX[ddx])
                first = False
            if first:
                return self.mathType(0.0)
            return self.memoizeXsimple[(x, dx)]
        else:
            if cons != None:
                self.consensus = cons
            keyX = (x, dx)
            if keyX in self.memoizeX[self.consensus]:
                valX = self.memoizeX[self.consensus][keyX]
                return valX
            else:
                hmm = self.factory.getHMM(self.consensus)
                valX = hmm.getProbabilities(X, x, dx)
                for ddx in range(dx + 1):
                    self.memoizeX[self.consensus][(x, ddx)] = valX[ddx]
            return valX[dx]

    def emissionY(self, Y, y, dy, cons=None):
        if self.merge_consensus or self.correctly_merge_consensus:
            keyY = (y, dy)
            if keyY in self.memoizeYsimple:
                return self.memoizeYsimple[keyY]
            cons_list = self.cons_list
            if cons != None:
                cons_list = cons
            first = True
            fun = lambda x:x
            if self.correctly_merge_consensus:
                fun = lambda x:[x]
            for consensus in cons_list:
                hmm = self.factory.getHMM(consensus)
                valY = hmm.getProbabilities(Y, y, dy)
                for ddy in range(dy + 1):
                    if first:
                        self.memoizeYsimple[(y, ddy)] = fun(valY[ddy])
                    else:
                        self.memoizeYsimple[(y, ddy)] += fun(valY[ddy])
                first = False
            if first:
                return self.mathType(0.0)
            return self.memoizeYsimple[(y, dy)]
        else:
            if cons != None:
                self.consensus = cons
            keyY = (y, dy)
            if keyY in self.memoizeY[self.consensus]:
                valY = self.memoizeY[self.consensus][keyY]
                self.y_count += 1
                return valY
            else:
                hmm = self.factory.getHMM(self.consensus)
                valY = hmm.getProbabilities(Y, y, dy)
                for ddy in range(dy + 1):
                    self.memoizeY[self.consensus][(y, ddy)] = valY[ddy]
            return valY[dy]

    def emission(self, X, x, dx, Y, y, dy):
        #print "Emission", (x, dx), (y, dy), "Len", (len(X), len(Y))
        # we expect that we have consensus from last generated duration 
        # TODO: fix distribution
        if self.correctly_merge_consensus:
            return sum([
                a * b 
                for a, b 
                in zip(self.emissionX(X, x, dx), self.emissionY(Y, y, dy))
            ])
        return self.emissionX(X, x, dx) * self.emissionY(Y, y, dy)

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
        dx , dy = 0, 0
        while len(consensus) * 3 > min(dx, dy):
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
        #TODO: this is broken
        for consensus in self.getCons(x, dx, y, dy):
            keyX = (x, dx)
            keyY = (y, dy)
            prob = self.mathType(1.0)
            if keyX in self.memoizeX[consensus]:
                prob *= self.memoizeX[consensus][keyX]
            if keyY in self.memoizeY[consensus]:
                prob *= self.memoizeY[consensus][keyY]
            ret[consensus] += prob 
        #print X[x:x + dx], Y[y:y + dy], tuple(ret.iteritems())
        return X[x:x + dx], Y[y:y + dy], tuple(ret.iteritems())
    
    def clearCache(self):
        self.memoizeX = defaultdict(dict)
        self.memoizeY = defaultdict(dict)
        #self.dgmemoize = dict()
        #self.rdgmemoize = dict()
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
        it = list(expectations.iteritems())
        shuffle(it)
        for (x, y, consensus), prob in it[:10000]:
            clen = len(consensus)
            hmm = self.getModel(consensus)
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
        print 'Trained values'
        print transitions, emissions, like
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

    def expand(self, params=None):
        if params == None:
            raise "Houston, we have a problem"
        consensuses = params['consensus']
        prefix_t = self.stateName + '_{}_'
        prefix_i = 0
        states = list()
        transitions = list()
        init = self.stateName + '_Init'
        end = self.stateName + '_End'
        total = 0.0
        for consensus in consensuses:
            prefix = prefix_t.format(prefix_i)
            prefix_i += 1
            model = self.factory.getHMM(consensus)
            probability = self.consensusDistribution[consensus]
            total += probability
            transitions.extend([
                {
                    'from': init,
                    'to': prefix + 'Init',
                    'prob': probability,
                },
                {
                    'from': prefix + 'End',
                    'to': end,
                    'prob': 1.0,
                },
            ])
            json = model.toJSON()
            st = json['states']
            for i in range(len(st)):
                st[i]['name'] = prefix + st[i]['name']
            states.extend(st)
            transitions.extend(map(
                lambda x: {
                    'from': prefix + x['from'],
                    'to': prefix + x['to'],
                    'prob': x['prob'],
                },
                json['transitions'],
            ))
        transitions.append({
            'from': init,
            'to': init,
            'prob': 1.0 - total,
        })
        template = {
            '__name__': 'GeneralizedState',
            'name': init,
            'startprob': 1.0,
            'endprob': 0.0,
            'emission': [('', mathType(1.0))],
            'durations': [(0, mathType(1.0))],
        }
        st = GeneralizedState(self.mathType)
        st.load(template)
        states.append(st.toJSON())
        template['name'] = end
        template['startprob'] = 0.0
        template['endprob'] = 1.0
        st = GeneralizedState(self.mathType)
        st.load(template)
        states.append(st.toJSON())
        return states, transitions, init, end
