from hmm.HMM import State
from hmm.GeneralizedHMM import GeneralizedState, GeneralizedHMM
import math
from tools.Exceptions import ParseException

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
    output = []
    if "alphabet" not in dictionary:
        raise ParseException("Alphabet not found for JC model")
    if "time" not in dictionary:
        raise ParseException("Time not found for JC model")
    alphabet = dictionary["alphabet"]
    time = dictionary["time"]
    for c in alphabet:
        for (cc, prob) in JCModel(c, time, alphabet):
            output.append(((c, cc), mathType(prob / 4.0)))
    return output       

def BackgroundProbabilityGenerator(dictionary, mathType):
    if "alphabet" not in dictionary:
        raise ParseException("Alphabet not found in background probability")
    tracks = 1
    track = 0
    if "track" in dictionary:
        track = dictionary['track']
    if "tracks" in dictionary:
        tracks = dictionary['tracks']
    alphabet = dictionary['alphabet']
    p = mathType(1.0 / float(len(alphabet)))
    output = []
    for c in alphabet:
        if tracks == 1:
            output.append((c, p))
        else:
            cc = [""]*tracks
            cc[track] = c
            output.append((tuple(cc), p))
    return output


def createProfileHMM(mathType, consensus, time, backgroundProb, trans):
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
        "endprob": 0.0
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
    return hmm