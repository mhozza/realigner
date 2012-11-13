from collections import defaultdict
import Graphs
from ConfigFactory import ConfigObject
from Exceptions import ParseException

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
        self.stateName = dictionary["name"]
        self.startProbability = self.mathType(dictionary["startprob"])
        self.endProbability = self.mathType(dictionary["endprob"])
        self.emissions = dict()
        for [key, prob] in dictionary["emission"]:
            if key.__class__.__name__ == "list":
                key = tuple(key)
            self.emissions[key] = self.mathType(prob)
            
                    
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
        self.mathType = mathType
        self.stateID = -1
        self.stateName = ""
        self.transitions = list()
        self.reverseTransitions = list()
        self.emissions = defaultdict(self.mathType)
        self.startProbability = self.mathType(0.0)
        self.endProbability = self.mathType(0.0)
        

    def durationGenerator(self):
        yield((1, self.mathType(1.0)))

    def emission(self, X, x):
        return self.emissions[X[x]]
    
    def setStateID(self, stateID):
        self.stateID = stateID
        
    def getStateID(self):
        return self.stateID
    
    def addTransition(self, stateID):
        self.transitions.append(stateID)
    
    def addReverseTransition(self, stateID):
        self.reverseTransitions.append(stateID)
    
    def clearTransitions(self):
        self.transitions = list()
        
    def clearReverseTransitions(self):
        self.reverseTransitions = list()
        
    def remapIDs(self, ids):
        self.stateID = ids[self.stateID]
        self.transitions = map(lambda x:ids[x], self.transitions)
        self.reverseTransitions = map(lambda x:ids[x], self.reverseTransitions)
        
    def getStartProbability(self):
        return self.startProbability
    
    def getEndProbability(self):
        return self.endProbability
    
    def followingIDs(self):
        return self.transitions
    
    def previousIDs(self):
        return self.reverseTransitions

class HMM(ConfigObject):
        
    def load(self, dictionary):
        ConfigObject.load(self, dictionary)
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
            for (to, prob) in toDict.iteritems():
                ret.append({"from": src, "to": to, "prob": prob})
        dictionary["transitions"] = ret
        return dictionary
    
    
    def __init__(self, mathType = float):
        self.mathType = mathType
        self.transitions = defaultdict(dict)
        self.states = list()
        self.statenameToID = dict()
        self.__transitions = list()
        self.__reverse_transitions = list()
        
        
    def addState(self, state):
        state.setStateID(len(self.states))
        self.statenameToID[state.stateName] = state.getStateID()
        self.states.append(state)
        return len(self.states) - 1
    
    
    def addTransition(self, stateFrom, stateTo, probability):
        self.transitions[stateFrom][stateTo] = probability
        self.states[stateFrom].addTransition(stateTo)
        self.states[stateTo].addReverseTransition(stateFrom)
        
        
    def reorderStatesTopologically(self):
        reorder = Graphs.orderToDict(
            reversed(
                Graphs.toposort(self.transitions)))
        transitions = defaultdict(dict)
        for (key, value) in self.transitions.iteritems:
            newval = dict()
            for (k, v) in value:
                newval[reorder[k]] = v
            transitions[reorder[key]] = newval
        self.transitions = transitions
        self.statenameToID = list()
        for stateID in range(len(self.states)):
            self.states[stateID].remap(reorder)
            self.statenameToID[self.states[stateID].stateName] = stateID
            

    # This functions transfers dictionaries to lists, so it is a bit faster
    def optimize(self):
        # Vyrobi potrebne tabulky, aby sme vedeli rychlo pocitat
        self.__transitions = list()
        self.__reverse_transitions = list()
        for _ in range(len(self.states)):
            self.__transitions.append(list())
            self.__reverse_transitions.append(list())