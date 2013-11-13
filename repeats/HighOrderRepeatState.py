from hmm.HMM import State
from repeats.RepeatAlignmentState import PairRepeatState
from tools.Exceptions import ParseException
from tools.my_rand import dist_to_json
from hmm.SpecialHMMs import createKRepeatHMM
from collections import defaultdict
import json
from duplicity.tempdir import default
import math

class HighOrderRepeatState(PairRepeatState):

    def __init__(self, *p):
        PairRepeatState.__init__(self, *p)
        self.maxK = 0
        self.time = self.mathType(0.0)
        self.backgroundProb = []
        self.indelProb = self.mathType(0.0)
        self.indelExtProb = self.mathType(0.0)
        self.repeatProb = self.mathType(0.0)
        self.endProb = self.mathType(0.0)
        self.model = None
        self.memoize = dict()

    def load(self, dictionary):
        PairRepeatState.load(self, dictionary)
        if 'maxK' not in dictionary:
            raise ParseException('maxK was not found in state')
        self.maxK = int(dictionary['maxK'])
        if 'time' not in dictionary:
            raise ParseException('time was not found in state')
        self.time = float(dictionary['time'])
        if 'backgroundprob' not in dictionary:
            raise ParseException('backgroundprob was not found in state')
        self.backgroundProb = dictionary['backgroundprob']
        if 'indelprob' not in dictionary:
            raise ParseException('indelprob was not found in state')
        self.indelProb = dictionary['indelprob']
        if 'indelextprob' not in dictionary:
            raise ParseException('indelextprob was not found in state')
        self.indelExtProb = dictionary['indelextprob']
        if 'repeatprob' not in dictionary:
            raise ParseException('repeatprob was not found in state')
        self.repeatProb = dictionary['repeatprob']
        if 'endprob' not in dictionary:
            raise ParseException('endprob was not found in state')
        self.endProb = dictionary['endprob']
        self.model = createKRepeatHMM(
            self.mathType,
            self.maxK,
            self.time,
            self.backgroundProb,
            self.indelProb,
            self.indelExtProb,
            self.repeatProb,
            self.endProb,
        )

    def toJSON(self):
        ret = PairRepeatState.toJSON(self)
        ret['maxK'] = self.maxK
        ret['time'] = self.time
        ret['backgroundprob'] = dist_to_json(self.backgroundProb)
        ret['indelprob'] = self.indelProb
        ret['indelextprob'] = self.indelExtProb
        ret['repeatprob'] = self.repeatProb
        ret['endprob'] = self.endProb
        return ret

    def getEmission(self, X, x, dx, tp):
        sv = (x, dx, tp)
        if sv in self.memoize:
            return self.memoize[sv]
        ret = self.model.getProbabilities(X, x, dx)
        for ddx in range(dx + 1):
            self.memoize[(x, ddx, tp)] = ret[ddx]
        return ret[dx]

    def emissionX(self, X, x, dx, cons_list):
        return self.getEmission(X, x, dx, 0)

    def emissionY(self, X, x, dx, cons_list):
        return self.getEmission(X, x, dx, 1)
    
    def emission(self, X, x, dx, Y, y, dy):
        xp = self.getEmission(X, x, dx, 0)
        yp = self.getEmission(Y, y, dy, 1)
        return xp * yp

    def buildSampleEmission(self):
        return None

    def sampleEmission(self):
        return None
    
    def trainModel(self, sequences):
        
        while True:
            # Do BW counts
            end = self.mathType(0.0)
            notEnd = self.mathType(0.0)
            transitions = [defaultdict(self.mathType)
                           for _ in range(len(self.model.states))]
            emissions = [defaultdict(self.mathType)
                         for _ in range(len(self.model.states))]
            for sequence in sequences:
                trans, emi, prob = self.model.getBaumWelchCount(
                    sequence,
                    0,
                    len(sequence)
                )
                end += prob
                notEnd += prob * len(sequence)
                for i in len(trans):
                    for k, p in trans[i].iteritems():
                        transitions[i][k] += prob * p
                for i in len(emi):
                    for k, p in emi[i].iteritems():
                        emissions[i][k] += prob * p
            print json.dumps(transitions, sort_keys=True, indent=4)
            print json.dumps(emissions, sort_keys=True, indent=4)
            # Estimate new parameters
            newParam = defaultdict(lambda *x:self.mathType(0.0))
            def name_wat(name):
                return name[0]
            for fr in range(len(transitions)):
                fr_name = name_wat(self.model.states[fr].stateName)
                for to, p in transitions[fr].iteritems():
                    to_name = name_wat(self.model.states[to].stateName)
                    newParam[fr_name + to_name] += p
            self.repeatProb = newParam['IR'] / newParam['II']
            self.endProb = end / notEnd
            self.indelExtProb = newParam['SS'] / newParam['SR']
            self.indelProb = newParam['RS'] / newParam['RR'] / self.mathType(2.0)
            self.time = self.time
            same = 0
            notSame = 0
            for i in range(len(emissions)):
                for k, _ in emissions[i].iteritems():
                    if len(k) == 2:
                        if k[0] == k[1]:
                            same += 1
                        else:
                            notSame += 1
            A = float(same) / float(same + notSame)
            self.time = - 3.0 / 4.0 * math.log((A - 0.25) / 0.75)
            # Create new model
            self.load(self.toJSON())