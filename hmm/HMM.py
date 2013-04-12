from collections import defaultdict
from algorithm import Graphs
from tools.ConfigFactory import ConfigObject
from tools.Exceptions import ParseException
from tools.my_rand import rand_generator
from tools.tuplemetrics import tadd, tlesssome

class State(ConfigObject):
        
    def load(self, dictionary):
        ConfigObject.load(self, dictionary)
        if "emission" not in dictionary:
            raise ParseException("Emission not found in state")
        if "name" not in dictionary:
            raise ParseException("Name not found in state")
        if "startprob" not in dictionary:
            raise ParseException("startprob not found in state")
        if "endprob" not in dictionary:
            raise ParseException("endprob not found in state")
        if "serialize" in dictionary:
            self.serialize = dictionary["serialize"]
        self.stateName = dictionary["name"]
        if "onechar" in dictionary:
            if len(dictionary['onechar']) != 1:
                raise ParseException('onechar has wrong length')
            self.onechar = dictionary["onechar"]
        else:
            if len(self.stateName) > 0:
                self.onechar = self.stateName[0]
            else:
                self.onechar = "?" 
        self.startProbability = self.mathType(dictionary["startprob"])
        self.endProbability = self.mathType(dictionary["endprob"])
        self.emissions = dict()
        for [key, prob] in dictionary["emission"]:
            if key.__class__.__name__ == "list":
                key = tuple(key)
            self.emissions[key] = self.mathType(prob)
    
    
    def buildSampleEmission(self):
        self._sampleEmission = rand_generator(self.emissions)
        
        
    def sampleEmission(self):
        return self._sampleEmission()
    
                    
    def toJSON(self):
        ret = ConfigObject.toJSON(self)
        ret["name"] = self.stateName
        ret["emission"] = list()
        ret["startprob"] = self.startProbability
        ret["endprob"] = self.endProbability
        for (key, prob) in self.emissions.iteritems():
            ret["emission"].append((key, prob))
        return ret
        
    
    def __init__(self, mathType = float):
        self.serialize = True
        self.mathType = mathType
        self.stateID = -1
        self.stateName = ""
        self.onechar = "?"
        self.transitions = list()
        self.reverseTransitions = list()
        self.emissions = defaultdict(self.mathType)
        self.startProbability = self.mathType(0.0)
        self.endProbability = self.mathType(0.0)
        self._sampleEmission = None

        

    def serializeMe(self):
        return self.serialize


    def durationGenerator(self):
        yield((1, self.mathType(1.0)))


    def emission(self, X, x, _=1):
        return self.emissions[X[x]]

    
    def setStateID(self, stateID):
        self.stateID = stateID

        
    def getStateID(self):
        return self.stateID

    
    def addTransition(self, stateID, prob):
        self.transitions.append((stateID, self.mathType(prob)))

    
    def addReverseTransition(self, stateID, prob):
        self.reverseTransitions.append((stateID, self.mathType(prob)))

    
    def clearTransitions(self):
        self.transitions = list()
        self.reverseTransitions = list()

    def normalizeTransitions(self):
        if len(self.transitions) == 0:
            return
        total = sum([p for _, p in self.transitions])
        self.transitions = [(state, prob/total) 
                            for state, prob in self.transitions]  
        self.reverseTransitions = [(state, prob/total) 
                                   for state, prob in self.reverseTransitions]  

 
    def followingIDs(self):
        return self.transitions

    
    def previousIDs(self):
        return self.reverseTransitions

        
    def remapIDs(self, ids):
        self.stateID = ids[self.stateID]
        self.transitions = map(lambda x:(ids[x[0]], x[1]), self.transitions)
        self.reverseTransitions = map(lambda x:(ids[x[0]], x[1]), 
                                      self.reverseTransitions)

        
    def getStartProbability(self):
        return self.startProbability

    
    def getEndProbability(self):
        return self.endProbability
    
    def getChar(self):
        return self.onechar
 

class HMM(ConfigObject):
    
    
    def __init__(self, mathType = float):
        self.mathType = mathType
        self.transitions = defaultdict(dict)
        self.states = list()
        self.statenameToID = dict()
        self.__transitions = list()
        self.__reverse_transitions = list()
        self.transitionsSampler = None
        self.initStateSampler = None
    
    
    def sampleTransition(self, state):
        return self.transitionsSampler[state]()
    
    
    def buildSampleTransitions(self):
        self.transitionsSampler = dict()
        for (key, value) in self.transitions.iteritems():
            self.transitionsSampler[key] = rand_generator(value)
        for stateID in range(len(self.states)):
            self.states[stateID].buildSampleEmission()
        self.initStateSampler = rand_generator(
            [(float(self.states[i].getStartProbability()), i) 
             for i in range(len(self.states))]
        )
    
        
    def load(self, dictionary):
        ConfigObject.load(self, dictionary)
        self.loadStates(dictionary)
        self.loadTransitions(dictionary)
            
    
    def loadStates(self, dictionary):
        if "states" not in dictionary:
            raise ParseException("states are missing in HMM object")
        for state in dictionary["states"]:
            self.addState(state)
        
        
    def loadTransitions(self, dictionary):
        if "transitions" not in dictionary:
            raise ParseException("transitions are missing in HMM object")  
        for transition in dictionary["transitions"]:
            if "from" not in transition or \
               "to" not in transition or \
               "prob" not in transition:
                raise ParseException("transitions are not properly defined")
            f = self.statenameToID[transition["from"]]
            t = self.statenameToID[transition["to"]]
            p = self.mathType(transition["prob"])
            self.addTransition(f, t, p)      
    
    
    def toJSON(self):
        ret = ConfigObject.toJSON(self)
        ret = self.statesToJSON(ret)
        ret = self.transitionsToJSON(ret)
        return ret
    
    
    def statesToJSON(self, dictionary):
        ret = list()
        for state in self.states:
            ret.append(state.toJSON())
        dictionary["states"] = ret
        return dictionary
    
    
    def transitionsToJSON(self, dictionary):
        ret = list()
        for (src, toDict) in self.transitions.iteritems():
            if not self.states[src].serializeMe():
                continue
            for (to, prob) in toDict.iteritems():
                if not self.states[to].serializeMe():
                    continue
                _src = self.states[src].stateName
                _to = self.states[to].stateName
                ret.append({"from": _src, "to": _to, "prob": prob})
        dictionary["transitions"] = ret
        return dictionary
      
      
    def addState(self, state):
        state.setStateID(len(self.states))
        self.statenameToID[state.stateName] = state.getStateID()
        self.states.append(state)
        return len(self.states) - 1
    
    
    def addTransition(self, stateFrom, stateTo, probability):
        probability = self.mathType(probability)
        self.transitions[stateFrom][stateTo] = probability
        self.states[stateFrom].addTransition(stateTo, probability)
        self.states[stateTo].addReverseTransition(stateFrom, probability)
        
    def clearTransitions(self):
        self.transitions = defaultdict(dict)
        for state in self.states:
            state.clearTransitions()
        
        
    def reorderStatesTopologically(self):
        reorder = Graphs.orderToDict(
            reversed(
                Graphs.toposort(self.transitions)))
        transitions = defaultdict(dict)
        for (key, value) in self.transitions.iteritems():
            newval = dict()
            for (k, v) in value.iteritems():
                newval[reorder[k]] = v
            transitions[reorder[key]] = newval
        self.transitions = transitions
        self.statenameToID = dict()
        for stateID in range(len(self.states)):
            self.states[stateID].remapIDs(reorder)
            self.statenameToID[self.states[stateID].stateName] = stateID
        newstates = list(self.states)
        for state in self.states:
            newstates[state.getStateID()] = state
        self.states = newstates
        
    def generateSequence(self, seq_len, generateLength=False):
        #TODO: nefunguje pre viacrozmerne a generalizovane HMM (pre silent stavy
        #      to funguje) a ak vsetky stavy su koncove. Aby to fungovalo je 
        #      treba zlozitejsi algoritmus (ak chceme specifikovat dlzku)
        if type(seq_len)==int:
            seq_len = tuple([seq_len])
        else:
            seq_len = tuple(seq_len)
        dim = len(seq_len)
        gen_len = tuple([0] * dim)
        state = self.initStateSampler()
        ret = list()
        zero = self.mathType(0.0)
        def condition():
            if generateLength:
                return not self.states[state].endProbability > zero
            return tlesssome(gen_len, seq_len)
        while condition():
            em = self.states[state].sampleEmission()
            if dim == 1:
                gen_len = tuple([gen_len[0] + len(em)])
            else:
                gen_len = tadd(gen_len, tuple([len(x) 
                                               for x in em 
                                               if type(x) != tuple]))
            ret.append((em, state))
            state = self.sampleTransition(state)
        return ret
