from hmm.HMM import State
from repeats.RepeatAlignmentState import PairRepeatState
from tools.Exceptions import ParseException
from tools.my_rand import dist_to_json
from hmm.SpecialHMMs import createKRepeatHMM
from collections import defaultdict
from algorithm.LogNum import LogNum
import json
import math
from copy import deepcopy
from hmm.hmm_transform import double_track_hmm

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
        if 'silendprob' not in dictionary:
            self.silEndProb = self.endProb
        else:   
            self.silEndProb = dictionary['silendprob']
        if 'initendprob' not in dictionary:
            self.initEndProb = self.endProb
        else:
            self.initEndProb = dictionary['initendprob']
        self.model = createKRepeatHMM(
            self.mathType,
            self.maxK,
            self.time,
            self.backgroundProb,
            self.indelProb,
            self.indelExtProb,
            self.repeatProb,
            self.endProb,
            self.initEndProb,
            self.silEndProb,
        )

    def toJSON(self):
        ret = PairRepeatState.toJSON(self)
        del ret['consensusdistribution']
        ret['maxK'] = self.maxK
        ret['time'] = self.time
        ret['backgroundprob'] = dist_to_json(self.backgroundProb)
        ret['indelprob'] = self.indelProb
        ret['indelextprob'] = self.indelExtProb
        ret['repeatprob'] = self.repeatProb
        ret['endprob'] = self.endProb
        ret['silendprob'] = self.silEndProb
        ret['initendprob'] = self.initEndProb
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
       
        iteration = 0
        for _ in range(12):
            iteration += 1
            print 'Iteration {}'.format(iteration)
            def model_to_dot(model):
                
                nodes = []
                edges = []

                for state in model.states:
                    em_strs = []
                    for k, v in state.emissions.iteritems():
                        em_strs.append("""'{}': {:.5}""".format(k, float(v)))
                    nodes.append("""
                 {name} [
                    shape="record"
                    label="{name2} | {emissions}"
                 ];
                """.format(name=state.stateName, name2=state.stateName, emissions=len(em_strs))
                )
                for f, x in model.transitions.iteritems():
                    for t, p in model.transitions[f].iteritems():
                        edges.append(""" 
                        {f} -> {t} [label="{p:.5}"];
                        """.format(f=model.states[f].stateName, t=model.states[t].stateName, p=float(p)))
                dot = """digraph {{
                {}
                {}
            }}""".format('\n'.join(nodes), '\n'.join(edges))
                return dot;
            with open('mmm.{}.dot'.format(iteration), 'w') as f:
                f.write(model_to_dot(self.model))
            # Do BW counts
            end = self.mathType(0.0)
            notEnd = self.mathType(0.0)
            transitions = [defaultdict(lambda *x:self.mathType(0.0))
                           for _ in range(len(self.model.states))]
            emissions = [defaultdict(lambda *x:self.mathType(0.0))
                         for _ in range(len(self.model.states))]
            sn = 0
            for sequence in sequences[:10]:
                sn += 1
                trans, emi, prob = self.model.getBaumWelchCount(
                    sequence,
                    0,
                    len(sequence)
                )
                end += prob
                notEnd += prob * len(sequence)
                for i in range(len(trans)):
                    for k, p in trans[i].iteritems():
                        transitions[i][k] += prob * p
                for i in range(len(emi)):
                    for k, p in emi[i].iteritems():
                        emissions[i][k] += prob * p
            # Estimate new parameters
            newParam = defaultdict(lambda *x:self.mathType(0.0))
            def name_wat(name):
                #if name=='I10': return 'X'
                return name[0]
            stateProb = defaultdict(lambda *x:self.mathType(0.0))
            for fr in range(len(transitions)):
                fr_name = name_wat(self.model.states[fr].stateName)
                for to, p in transitions[fr].iteritems():
                    if p != p:
                        # skip Nan
                        continue
                    to_name = name_wat(self.model.states[to].stateName)
                    newParam[fr_name + to_name] += p
                    stateProb[self.model.states[fr].stateName] += p
                    stateProb[self.model.states[to].stateName] += p
            print 'IR: {} II: {} II+IR: {}'.format(newParam['IR'], newParam['II'], newParam['II'] + newParam['IR'])
            def smooth(x):
                if x < 0.01:
                    return self.mathType(0.01)
                if x > 0.99:
                    return self.mathType(0.99)
                return x
            I_all = newParam['II'] + newParam['IR'] + newParam['IE']
            S_all = newParam['SR'] + newParam['SS'] + newParam['SE']
            R_all = newParam['RR'] + newParam['RS'] + newParam['RE']
            self.repeatProb = smooth(newParam['IR'] / I_all) 
            self.endProb = smooth(newParam['RE'] / R_all)
            self.silEndProb = smooth(newParam['SE'] / S_all)
            self.initEndProb = smooth(newParam['IE'] / I_all)
            self.indelExtProb = smooth(newParam['SS'] / S_all)
            self.indelProb = smooth(newParam['RS'] / R_all / self.mathType(2.0))
            self.time = self.time
            print 'repeatProb={} {{,sil,init}}endProb={}/{}/{} indelExtProb={} indelProb={} prev_time={} emission='.format(self.repeatProb, self.endProb, self.silEndProb, self.initEndProb, self.indelExtProb, self.indelProb, self.time, (self.model.states[self.model.statenameToID['R1']].__dict__))
            kkk = max(stateProb.values())
            for k in stateProb: stateProb[k] = float(stateProb[k])/float(kkk)
            dede = list()
            for k in stateProb: 
                if k[0] == 'S': 
                    dede.append(k)
            for k in dede: stateProb[k]
            print json.dumps([stateProb], sort_keys=True)
            same = 0
            notSame = 0
            for i in range(len(emissions)):
                for k, p in emissions[i].iteritems():
                    if len(k) == 2:
                        if k[0] == k[1]:
                            same += p
                        else:
                            notSame += p
            A = same / (same + notSame)
            add = same + notSame
            print same/add, notSame/add, A
            if A <= 0.25: A = 0.25001
            self.time = - 3.0 / 4.0 * math.log((A - 0.25) / 0.75)
            if self.time < 0.005:
                self.time = 0.005
            # Create new model
            js = self.toJSON()
            self.load(js)
       
    def expand(self, _=None):
        json = self.model.toJSON()
        prefix = self.stateName + '_'

        states = map(deepcopy, self.model.states)
        for i in range(len(states)):
            states[i].stateName = prefix + states[i].stateName
        transitions = map(
            lambda x: {
                'from': prefix + x['from'],
                'to': prefix + x['to'],
                'prob': x['prob'],
            },
            json['transitions'],
        )
        return double_track_hmm(states, transitions, prefix + 'I1', prefix + 'End', self.mathType)
