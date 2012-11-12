from collections import defaultdict
import Graphs
from ConfigFactory import ConfigObject

class State(ConfigObject):
        
    def load(self, dictionary):
        ConfigObject.load(self, dictionary)
        if "emission" not in dictionary:
            raise "Emission not found in state"
        if "name" not in dictionary:
            raise "Name not found in state"
        self.stateName = dictionary["name"]
        for (key, prob) in dictionary["emission"].iteritems():
            self.emission[key] = float(prob)
            
                    
    def toJSON(self):
        ret = ConfigObject.toJSON(self)
        ret["name"] = self.stateName
        for (key, prob) in self.emission.iteritems():
            ret["emission"][key] = float(prob)
        
    
    def __init__(self):
        self.stateID = -1
        self.stateName = ""
        self.transitions = list()
        self.reverseTransitions = list()
        self.emission = defaultdict(float)

    def durationGenerator(self):
        yield((1,1.0))

    def emission(self, X, x):
        return self.emission[X[x]]
    
    def setStateID(self, stateID):
        self.stateID = stateID
    
    def addTransition(self, stateID):
        self.transitions.append(stateID)
    
    def addReverseTransitions(self, stateID):
        self.reverseTransitions.append(stateID)
    
    def clearTransitions(self):
        self.transitions = list()
        
    def clearReverseTransitions(self):
        self.reverseTransitions = list()
        
    def remapIDs(self, ids):
        self.stateID = ids[self.stateID]
        self.transitions = map(lambda x:ids[x], self.transitions)
        self.reverseTransitions = map(lambda x:ids[x], self.reverseTransitions)
    
    def followingIDs(self):
        return self.transitions
    
    def previousIDs(self):
        return self.reverseTransitions

class HMM(ConfigObject):
        
    def load(self, dictionary):
        self.__init__(self)
        ConfigObject.load(self, dictionary)
        self.loadStates(dictionary)
        self.loadTransitions(dictionary)
            
    
    def loadStates(self, dictionary):
        if "states" not in dictionary:
            raise "states are missing in HMM object"
        for state in dictionary["states"]:
            self.addState(state)
        
        
    def loadTransitions(self, dictionary):
        if "transitions" not in dictionary:
            raise "transitions are missing in HMM object"  
        for transition in dictionary["transitions"]:
            if "from" not in transition or \
               "to" not in transition or \
               "prob" not in transition:
                raise "transitions are not properly defined"
            f = self.translateState(transition["from"])
            t = self.translateState(transition["to"])
            p = float(transition["prob"])
            self.addTransition(f, t, p)      
    
    
    def toJSON(self):
        ret = ConfigObject.toJSON(self)
        ret = self.statesToJSON(ret)
        ret = self.transitionsToJSON(ret)
        return ret
    
    
    def statesToJSON(self, dictionary):
        ret = list();
        for state in self.states:
            ret.append(state.toJSON())
        dictionary["states"] = ret;
        return dictionary
    
    
    def transitionsToJSON(self, dictionary):
        ret = list()
        for (src, toDict) in self.transitions.iteritems():
            for (to, prob) in toDict.iteritems():
                ret.add({"from": src, "to": to, "prob": prob})
        dictionary["transitions"] = ret
        return dictionary
    
    
    def __init__(self):
        print "HMM.__init__"
        self.transitions = defaultdict(dict)
        self.states = list()
        
        
    def addState(self, state):
        state.setID(len(list))
        list.append(state)
        return len(list) - 1
    
    
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
        self.transitions = transitions;
        for stateID in range(len(self.states)):
            self.states[stateID].remap(reorder)


    # This functions transfers dictionaries to lists, so it is a bit faster        
    def optimize(self):
        return
    