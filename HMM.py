from collections import defaultdict
import Graphs

class State:
    
    def __init__(self):
        self.stateID = -1
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

class HMM:
    
    def __init__(self):
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
    