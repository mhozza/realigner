import unittest
from LogNum import LogNum
from HMM import State, HMM

def toLogNum(L):
    return [LogNum(f) for f in L]
    

class ConfigFactoryTest(unittest.TestCase):
    
            
    def __init__(self, *p):
        unittest.TestCase.__init__(self, *p)
        self.Y = None
        self.inputY = None
        self.mathTypes = [float, LogNum]
        
    
    def setUp(self):
        self.inputY = {
            "__name__": "State",
            "name": "name",
            "startprob": 1.0,
            "emission": [("A", 1.0), (["C", "D"], 0.5)],
            "endprob": 0.5
        } 
        Y = self.inputY
        Y["emission"][1] = (tuple(Y["emission"][1][0]), Y["emission"][1][1])
        self.Y = Y
        self.inputHMMData = dict()
        
        for mathType in self.mathTypes:
             
            hmmInit = {
                "__name__": "HMM",
                "states": [],
                "transitions": [
                    {"from": "Init", "to": "White", "prob": mathType(0.3)},
                    {"from": "Init", "to": "Black", "prob": mathType(0.7)},
                    {"from": "White", "to": "White", "prob": mathType(1.0)},
                    {"from": "Black", "to": "Black", "prob": mathType(1.0)}
                ]
            }
            Init = State(mathType)
            Init.load({
                "__name__": "State",
                "name": "Init",
                "startprob": 1.0,
                "endprob": 1.0,
                "emission": [("0", 0.5), ("1", 0.5)]
            })
            White = State(mathType)
            White.load({
                "__name__": "State",
                "name": "White",
                "startprob": 0.0,
                "endprob": 1.0,
                "emission": [("0", 0.05), ("1", 0.95)]
            })
            Black = State(mathType)
            Black.load({
                "__name__": "State",
                "name": "Black",
                "startprob": 0.0,
                "endprob": 1.0,
                "emission": [("0", 0.9), ("1", 0.1)]
            })
            hmmInit["states"] = [White, Init, Black]
            self.inputHMMData[mathType] = hmmInit
        
            
    def test_state_loading(self):
        a = State()
        a.load(self.inputY)
        X = a.toJSON()
        Y = self.Y
        self.assertDictEqual(X, Y, "Loading and dumping to JSON does not " + \
                             " work: " + str(X) + " != " + str(Y))
    
            
    def test_state(self):
        for numType in self.mathTypes:
            state = State(numType)
            state.load(self.inputY)
            #test duration
            X = list(state.durationGenerator())
            Y = [(1, numType(1.0))]
            self.assertEqual(X, Y, "HMM.durationGenerator() does not work: " + \
                             str(X) + " != " + str(Y))
            #test emission
            Y = numType(1.0)
            X = state.emission("AC", 0)
            self.assertAlmostEqual(X, Y, delta=1e-7, 
                                   msg="HMM.emission(\"AC\", 0) does not " + \
                                   "work: " + str(X) + " != " + str(Y))
            #test stateID
            for Y in range(4):
                state.setStateID(Y)
                X = state.getStateID()
                self.assertEqual(X, Y, "HMM.set/getStateID({0}) is broken." \
                                 .format(Y))
            #test transitions & remap
            transitions = [(1, 1.0), (2, 0.4), (3, 0.2), (4, 0.6)]
            M = {1: 2, 2: 3, 3: 4, 4: 5}
            for (x, p) in transitions:
                state.addTransition(x, p)
                state.addReverseTransition(x, p)
            X = state.followingIDs()
            Y = transitions
            self.assertEqual(X, Y, "HMM.?transitions are not working.")
            X = state.previousIDs()
            self.assertEqual(X, Y, "HMM.?reverse transitions are not working.")
            state.remapIDs(M)
            transitions = [(M[x[0]], x[1]) for x in transitions]
            X = state.followingIDs()
            Y = transitions
            self.assertEqual(X, Y, "HMM.remapIDs() is not working.")
            X = state.previousIDs()
            self.assertEqual(X, Y, "HMM.remapIDs() is not working.")
            state.clearTransitions()
            Y = []
            X = state.followingIDs()
            X.extend(state.previousIDs())
            self.assertEqual(X, Y, "HMM.clearTransitions() is not working.")
        #test start & stop probability
        X = state.getStartProbability()
        Y = 1.0
        self.assertAlmostEqual(X, Y, delta=1e-7, 
                               msg="HMM.getStartProbability is broken.")
        X = state.getEndProbability()
        Y = 0.5
        self.assertAlmostEqual(X, Y, delta=1e-7, 
                               msg="HMM.getEndProbability is broken.")
        
    
    def test_HMM_load(self):
        for mathType in self.mathTypes:
            hmm = HMM(mathType)
            hmm.load(self.inputHMMData[mathType])
            X = hmm.toJSON()
            Y = self.inputHMMData[mathType]
            for i in range(len(Y["states"])):
                Y["states"][i] = Y["states"][i].toJSON()
            X["transitions"] = sorted(X["transitions"])
            Y["transitions"] = sorted(Y["transitions"])
            self.assertDictEqual(X, Y, "HMM.load/toJSON() is broken: " + \
                                 str(X) + " != " + str(Y)) 
        
    
    def test_HMM_toposort(self):
        for mathType in self.mathTypes:
            hmm = HMM(mathType)
            hmm.load(self.inputHMMData[mathType])
            hmm.reorderStatesTopologically()
            Y = "Init"
            X = hmm.states[0].stateName
            self.assertEqual(X, Y, "Toposort does no sort states correctly." + \
                             " First state is " + X + " and should be " + Y)
            self.assertEqual(len(hmm.transitions[0]), 2, 
                             "Remapping of transitions does not work.")
            self.assertEqual(len(hmm.transitions[1]), 1, 
                             "Remapping of transitions does not work.")
            self.assertEqual(len(hmm.transitions[2]), 1, 
                             "Remapping of transitions does not work.")
            for i in [1,2]:
                if i not in hmm.transitions[i]:
                    self.fail("Remapping of transitions does not work.")
                self.assertAlmostEqual(float(hmm.transitions[i][i]), 1.0,
                                       delta="1e-7", msg=
                                       "Remapping of transitions does not work")
                
   
if __name__ == '__main__':
    unittest.main()