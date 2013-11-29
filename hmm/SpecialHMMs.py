from hmm.HMM import State
from hmm.GeneralizedHMM import GeneralizedState, GeneralizedHMM
import math
from tools.Exceptions import ParseException
from collections import defaultdict
from tools.file_wrapper import Open
import json
from algorithm.LogNum import LogNum
import hashlib
from hmm.HighOrderState import HighOrderState

def JCModelDist(c1, c2, time):
    if c1 == c2:
        return 0.25 + 0.75 * math.exp(-4.0 / 3.0 * time)
    else:
        return 0.25 - 0.25 * math.exp(-4.0 / 3.0 * time)
        

def JCModel(char, time, outchars):
    output = []
    for c in outchars:
        output.append((c, JCModelDist(c, char, time)))
    return output
    

def JukesCantorGenerator(dictionary,  mathType):
    if "alphabet" not in dictionary:
        raise ParseException("Alphabet not found for JC model")
    if "timeX" not in dictionary or "timeY" not in dictionary:
        raise ParseException("Time not found for JC model")
    if "backgroundprob" not in dictionary:
        raise ParseException("backgroundprob not in JC model")
    alphabet = dictionary["alphabet"]
    timeX = dictionary["timeX"]
    timeY = dictionary["timeY"]
    background = dict()
    for (key, value) in dictionary["backgroundprob"]:
        background[key] = value
    dst = defaultdict(mathType)
    for c in alphabet:
        for (cc, prob) in JCModel(c, timeX, alphabet):
            for (ccc, prob2) in JCModel(c, timeY, alphabet):
                dst[(cc, ccc)] += background[c] * prob * prob2 
    return [x for x in dst.iteritems()]       


def BackgroundProbabilityGenerator(dictionary, mathType):
    if "alphabet" not in dictionary:
        raise ParseException("Alphabet not found in background probability")
    tracks = 1
    track = 0
    if "track" in dictionary:
        track = dictionary['track']
    if "tracks" in dictionary:
        tracks = dictionary['tracks']
    distribution = None
    if 'distribution' in dictionary:
        distribution = dict(dictionary['distribution'])
    alphabet = dictionary['alphabet']
    p = mathType(1.0 / float(len(alphabet)))
    output = []
    for c in alphabet:
        if distribution != None:
            p = distribution[c]
        if tracks == 1:
            output.append((c, p))
        else:
            cc = [""]*tracks
            cc[track] = c
            output.append((tuple(cc), p))
    return output


def createProfileHMMv1(mathType, consensus, time, backgroundProb, trans):
    length = len(consensus)
    states = []
    transitions = []
    for i in range(length):
        char = consensus[i]
        matchState = State(mathType)
        insertState = State(mathType)
        deleteState1 = GeneralizedState(mathType)
        deleteState2 = GeneralizedState(mathType)
        matchState.load({
            "__name__": "State",
            "name": "m" + str(i),
            "startprob": 0.0,
            "emission": JCModel(char, time, "ACGT"),
            "endprob": 1.0
        })
        insertState.load({
            "__name__": "State",
            "name": "i" + str(i),
            "startprob": 0.0,
            "emission": backgroundProb,
            "endprob": 1.0
        })
        deleteState1.load({
            "__name__": "GeneralizedState",
            "name": "1d" + str(i),
            "startprob": 0.0,
            "emission": [("", 1.0)],
            "endprob": 0.0,
            "durations": [(0, 1.0)]
        })
        deleteState2.load({
            "__name__": "GeneralizedState",
            "name": "2d" + str(i),
            "startprob": 0.0,
            "emission": [("", 1.0)],
            "endprob": 0.0,
            "durations": [(0, 1.0)]
        })
        states.extend([matchState, insertState, deleteState1, deleteState2])
        if i < length - 1:
            transitions.extend([
                {"from": "m" + str(i), "to": "m" + str(i + 1),
                 "prob": trans['MM']},
                {"from": "m" + str(i), "to": "i" + str(i + 1),
                 "prob": trans['MI']},
                {"from": "m" + str(i), "to": "1d" + str(i + 1),
                 "prob": trans['MD']},
                {"from": "1d" + str(i), "to": "1d" + str(i + 1),
                 "prob": trans['DD']},
                {"from": "1d" + str(i), "to": "m" + str(i + 1),
                 "prob": trans['DM']},
                {"from": "1d" + str(i), "to": "i" + str(i + 1),
                 "prob": trans['DI']},
                {"from": "2d" + str(i), "to": "2d" + str(i + 1),
                 "prob": trans['DD']},
                {"from": "2d" + str(i), "to": "m" + str(i + 1),
                 "prob": trans['DM']},
                {"from": "2d" + str(i), "to": "i" + str(i + 1),
                 "prob": trans['DI']},
            ])
        transitions.extend([
            {"from": "i" + str(i), "to": "i" + str(i), "prob": trans['II']},
            {"from": "i" + str(i), "to": "m" + str(i), "prob": trans['IM']},
            {"from": "i" + str(i), "to": "1d" + str(i), "prob": trans['ID']},
        ])
    transitions.extend([
        {"from": "Init", "to": "m0", "prob": trans['_M']},
        {"from": "Init", "to": "i0", "prob": trans['_I']},
        {"from": "Init", "to": "1d0", "prob": trans['_D']},
        {"from": "1d" + str(length - 1), "to": "m0", "prob": trans['_M']},
        {"from": "1d" + str(length - 1), "to": "i0", "prob": trans['_I']},
        {"from": "1d" + str(length - 1), "to": "2d0", "prob": trans['_D']},
        {"from": "m" + str(length - 1), "to": "Init", "prob": 1.0-trans['MI']},
        {"from": "m" + str(length - 1), "to": "i" + str(length),
         "prob": trans['MI']},
        {"from": "i" + str(length), "to": "i" + str(length),
         "prob": trans['II']},
        {"from": "i" + str(length), "to": "Init", "prob": 1.0 - trans['II']},
        {"from": "2d" + str(length - 1), "to": "m0",
         "prob": trans['_M'] / (trans['_M'] + trans['_I'])},
        {"from": "2d" + str(length - 1), "to": "i0",
         "prob": trans['_I'] / (trans['_M'] + trans['_I'])},
    ])
    insertState = State(mathType)
    insertState.load({
        "__name__": "State",
        "name": "i" + str(length),
        "startprob": 0.0,
        "emission": backgroundProb,
        "endprob": 1.0
    })
    states.append(insertState)
    initState = GeneralizedState(mathType)
    initState.load({
        "__name__": "GeneralizedState",
        "name": "Init",
        "startprob": 1.0,
        "emission": [("", 1.0)],
        "endprob": 1.0,
        "durations": [(0, 1.0)]
    })
    states.append(initState)
    hmm = GeneralizedHMM(mathType)
    hmm.load({
        "__name__": "GeneralizedHMM",
        "states": states,
        "transitions": transitions,
    })
    hmm.reorderStatesTopologically()
    nm = consensus
    if len(nm) > 20:
        nm = hashlib.md5(consensus).hexdigest()
    return hmm


def createProfileHMMv2(mathType, consensus, time, backgroundProb, trans):
    if consensus == None or len(consensus) == 0: 
        raise "Wrong consensus: {}".format(consensus)
    length = len(consensus)
    states = []
    transitions = []
    for i in range(length):
        char = consensus[i]
        matchState = State(mathType)
        insertState = State(mathType)
        deleteState1 = GeneralizedState(mathType)
        deleteState2 = GeneralizedState(mathType)
        matchState.load({
            "__name__": "State",
            "name": "m" + str(i),
            "startprob": 0.0,
            "emission": JCModel(char, time, "ACGT"),
            "endprob": 0.0
        })
        insertState.load({
            "__name__": "State",
            "name": "i" + str(i),
            "startprob": 0.0,
            "emission": backgroundProb,
            "endprob": 0.0
        })
        deleteState1.load({
            "__name__": "GeneralizedState",
            "name": "1d" + str(i),
            "startprob": 0.0,
            "emission": [("", 1.0)],
            "endprob": 0.0,
            "durations": [(0, 1.0)]
        })
        deleteState2.load({
            "__name__": "GeneralizedState",
            "name": "2d" + str(i),
            "startprob": 0.0,
            "emission": [("", 1.0)],
            "endprob": 0.0,
            "durations": [(0, 1.0)]
        })
        states.extend([matchState, insertState, deleteState1, deleteState2])
        if i < length - 1:
            transitions.extend([
                {"from": "m" + str(i), "to": "m" + str(i + 1),
                 "prob": trans['MM']},
                {"from": "m" + str(i), "to": "i" + str(i + 1),
                 "prob": trans['MI']},
                {"from": "m" + str(i), "to": "1d" + str(i + 1),
                 "prob": trans['MD']},
                {"from": "1d" + str(i), "to": "1d" + str(i + 1),
                 "prob": trans['DD']},
                {"from": "1d" + str(i), "to": "m" + str(i + 1),
                 "prob": trans['DM']},
                {"from": "1d" + str(i), "to": "i" + str(i + 1),
                 "prob": trans['DI']},
                {"from": "2d" + str(i), "to": "2d" + str(i + 1),
                 "prob": trans['DD']},
                {"from": "2d" + str(i), "to": "m" + str(i + 1),
                 "prob": trans['DM']},
                {"from": "2d" + str(i), "to": "i" + str(i + 1),
                 "prob": trans['DI']},
            ])
        transitions.extend([
            {"from": "i" + str(i), "to": "i" + str(i), "prob": trans['II']},
            {"from": "i" + str(i), "to": "m" + str(i), "prob": trans['IM']},
            {"from": "i" + str(i), "to": "1d" + str(i), "prob": trans['ID']},
        ])
    transitions.extend([
        {"from": "Init", "to": "m0", "prob": trans['_M']},
        {"from": "Init", "to": "i0", "prob": trans['_I']},
        {"from": "Init", "to": "1d0", "prob": trans['_D']},
        {"from": "Init", "to": "End", "prob": trans['_E']},
        {"from": "1d" + str(length - 1), "to": "m0", "prob": trans['DRM']},
        {"from": "1d" + str(length - 1), "to": "End", "prob": trans['DRE']},
        {"from": "1d" + str(length - 1), "to": "i0", "prob": trans['DRI']},
        {"from": "1d" + str(length - 1), "to": "2d0", "prob": trans['DRD']},
        {"from": "m" + str(length - 1), "to": "Init", "prob": trans['MR_']},
        {"from": "m" + str(length - 1), "to": "End", "prob": trans['MRE']},
        {"from": "m" + str(length - 1), "to": "i" + str(length), 
         "prob": trans['MRI']},
        {"from": "i" + str(length), "to": "i" + str(length),
         "prob": trans['IRI']},
        {"from": "i" + str(length), "to": "Init", "prob": trans['IR_']},
        {"from": "i" + str(length), "to": "End", "prob": trans['IRE']},
    ])
    insertState = State(mathType)
    insertState.load({
        "__name__": "State",
        "name": "i" + str(length),
        "startprob": 0.0,
        "emission": backgroundProb,
        "endprob": 0.0
    })
    states.append(insertState)
    initState = GeneralizedState(mathType)
    initState.load({
        "__name__": "GeneralizedState",
        "name": "Init",
        "startprob": 1.0,
        "emission": [("", 1.0)],
        "endprob": 0.0,
        "durations": [(0, 1.0)]
    })
    states.append(initState)
    endState = GeneralizedState(mathType)
    endState.load({
        "__name__": "GeneralizedState",
        "name": "End",
        "startprob": 0.0,
        "emission": [("", 1.0)],
        "endprob": 1.0,
        "durations": [(0, 1.0)],
    })
    states.append(endState)
    remstate = '2d' + str(length - 1)
    states = [state for state in states if state.stateName != remstate]
    transitions = [tran for tran in transitions 
                   if tran['to'] != remstate and tran['from'] != remstate]
    hmm = GeneralizedHMM(mathType)
    hmm.load({
        "__name__": "GeneralizedHMM",
        "states": states,
        "transitions": transitions,
    })
    for i in range(len(states)):
        hmm.states[i].normalizeTransitions()
    hmm.reorderStatesTopologically()
    nm = consensus
    if len(nm) > 20:
        nm = hashlib.md5(consensus).hexdigest()
    #with Open('submodels/{0}.js'.format(nm), 'w') as f:
    #    def LogNumToJson(obj):
    #        if isinstance(obj, LogNum):
    #            return '{0} {1}'.format(str(float(obj)),str(obj.value))
    #        raise TypeError
    #    json.dump(hmm.toJSON(), f, indent=4, sort_keys=True, 
    #              default=LogNumToJson)
    return hmm


def createKRepeatHMM(
    mathType,
    maxK,
    time,
    backgroundProb,
    indelProb,
    indelExtProb,
    repeatProb,
    endProb,
    initEndProb = None,
    silEndProb = None,
):
    if initEndProb == None:
        initEndProb = endProb
    if silEndProb == None:
        silEndProb = endProb
    tp  = type(backgroundProb)
    if tp in [dict, defaultdict]:
        backgroundProb = list(backgroundProb.iteritems())
    probabilities = list(backgroundProb)
    alphabet = [x for x, _ in backgroundProb]
    for a in alphabet:
        for b in alphabet:
            probabilities.append((a + b, JCModelDist(a, b, time)))
    states = list()
    transitions = list()
    
    end_state = GeneralizedState(mathType)
    end_state.load({
        '__name__': 'GeneralizedState',
        'name': 'End',
        'startprob': mathType(0.0),
        'endprob': mathType(1.0),
        'emission': [('', mathType(1.0))],
        'durations': [(0, mathType(1.0))],
    })
    states.append(end_state)

    initTemplate = {
        '__name__': 'GeneralizedState',
        'name': 'I{}',
        'startprob': mathType(0.0),
        'endprob': mathType(0.0),
        'emission': backgroundProb,#,[('', mathType(1.0))],#backgroundProb,
        'durations': [(1, mathType(1.0))],
    }
    
    for order in range(1, maxK + 1):
        if order == 1:
            initTemplate['startprob'] = mathType(1.0)
        transitions.append({
            'from': 'I{}'.format(order),
            'to': 'R{}'.format(order),
            'prob': repeatProb,
        })
        transitions.append({
            'from': 'I{}'.format(order),
            'to': 'End',
            'prob': initEndProb,
        })
        self_prob = mathType(1.0)
        self_prob -= repeatProb + initEndProb
        if order < maxK:
            transitions.append({
                'from': 'I{}'.format(order),
                'to': 'I{}'.format(order + 1),
                'prob': self_prob
            })
        initTemplate['name'] = 'I{}'.format(order)
        state = GeneralizedState(mathType)
        state.load(initTemplate)  
        states.append(state)
            
    silentTemplate = {
        '__name__': 'GeneralizedState',
        'name': 'S{}{}',
        'startprob': mathType(0.0),
        'endprob': mathType(0.0),
        'emission': [('', mathType(1.0))],
        'durations': [(0, mathType(1.0))],
    }
    
    insertTemplate = {
        '__name__': 'GeneralizedState',
        'name': 'S{}{}',
        'startprob': mathType(0.0),
        'endprob': mathType(0.0),
        'emission': backgroundProb, 
        'durations': [(1, mathType(1.0))],
    }

    for order in range(1, maxK):
        insertTemplate['name'] = 'SI{}'.format(order)
        state = GeneralizedState(mathType)
        state.load(insertTemplate)
        states.append(state)
        end_p = mathType(1.0)
        if order < maxK - 1:
            transitions.append({
                'from': 'SI{}'.format(order),
                'to': 'SI{}'.format(order + 1),
                'prob': indelExtProb
            })
            end_p -= indelExtProb
        transitions.append({
            'from': 'SI{}'.format(order),
            'to': 'End',
            'prob': silEndProb
        })
        end_p -= silEndProb
        transitions.append({
            'from': 'SI{}'.format(order),
            'to': 'R{}'.format(order + 1),
            'prob': end_p
        })
        silentTemplate['name'] = 'SD{}'.format(order)
        state = GeneralizedState(mathType)
        state.load(silentTemplate)
        states.append(state)
        end_p = mathType(1.0)
        transitions.append({
            'from': 'SD{}'.format(order),
            'to': 'End',
            'prob': silEndProb,
        })
        end_p -= silEndProb
        if order < maxK - 1:
            transitions.append({
                'from': 'SD{}'.format(order + 1),
                'to': 'SD{}'.format(order),
                'prob': indelExtProb
            })
        if order > 1:
            end_p -= indelExtProb
        transitions.append({
            'from': 'SD{}'.format(order),
            'to': 'R{}'.format(order),
            'prob': end_p
        })
    
    repeatTemplate = {
        '__name__': 'HighOrderState',
        'name': 'R{}',
        'startprob': mathType(0.0),
        'endprob': mathType(0.0),
        'emission': probabilities,
        'durations': [(1, mathType(1.0))],
        'order': 0
    }
    for order in range(1, maxK + 1):
        repeatTemplate['name'] = 'R{}'.format(order)
        repeatTemplate['order'] = order
        state = HighOrderState(mathType)
        state.load(repeatTemplate)
        states.append(state)
        stayprob = mathType(1.0)
        transitions.append({
            'from': 'R{}'.format(order),
            'to': 'End',
            'prob': endProb,
        })
        stayprob -= endProb
        if order > 1:
            transitions.append({
                'from': 'R{}'.format(order),
                'to': 'SD{}'.format(order - 1),
                'prob': indelProb,
            })
            stayprob -= indelProb
        if order < maxK:
            transitions.append({
                'from': 'R{}'.format(order),
                'to': 'SI{}'.format(order),
                'prob': indelProb,
            })
            stayprob -= indelProb
        transitions.append({
            'from': 'R{}'.format(order),
            'to': 'R{}'.format(order),
            'prob': stayprob,
        })
    hmm = GeneralizedHMM(mathType)
    hmm.load({
        '__name__': 'GeneralizedHMM',
        'states': states,
        'transitions': transitions,
    })
    for i in range(len(states)):
        hmm.states[i].normalizeTransitions()
    hmm.reorderStatesTopologically()
    with Open('submodels/newK-{}-{}-{}-{}.js'.format(maxK, time, indelProb, repeatProb), 'w') as f:
        print f
        def LogNumToJson(obj):
            if isinstance(obj, LogNum):
                return '{0}'.format(str(float(obj)))
            raise TypeError
        json.dump(
            hmm.toJSON(),
            f,
            indent=4,
            sort_keys=True, 
            default=LogNumToJson
        )
    return hmm
