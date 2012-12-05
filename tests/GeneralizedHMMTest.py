import unittest
from algorithm.LogNum import LogNum
from hmm.GeneralizedHMM import GeneralizedState, GeneralizedHMM

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
            "__name__": "GeneralizedState",
            "name": "name",
            "startprob": 1.0,
            "emission": [("0", 0.5), ("00", 0.5)],
            "endprob": 0.5,
            "durations": [(1, 0.5), (2, 0.5)]
        } 

        
        self.HMM = dict()
        
        for mathType in self.mathTypes:
             
            hmmInit = {
                "__name__": "GeneralizedHMM",
                "states": [],
                "transitions": [
                    {"from": "one", "to": "one", "prob": mathType(0.3)},
                    {"from": "one", "to": "two", "prob": mathType(0.7)},
                    {"from": "two", "to": "one", "prob": mathType(0.5)},
                    {"from": "two", "to": "two", "prob": mathType(0.5)}
                ]
            }
            one = GeneralizedState(mathType)
            one.load({
                "__name__": "GeneralizedState",
                "name": "one",
                "startprob": 0.2,
                "endprob": 1.0,
                "emission": [("0", 1.0), ("00", 1.0)],
                "durations": [(1, 0.5), (2, 0.5)]
            })
            two = GeneralizedState(mathType)
            two.load({
                "__name__": "GeneralizedState",
                "name": "two",
                "startprob": 0.8,
                "endprob": 1.0,
                "emission": [("0", 1.0), ("00", 1.0)],
                "durations": [(1, 0.5), (2, 0.5)]
            })
            hmmInit["states"] = [one, two]
            self.HMM[mathType] = GeneralizedHMM(mathType)
            self.HMM[mathType].load(hmmInit)
        
            
    def test_state_loading(self):
        a = GeneralizedState()
        a.load(self.inputY)
        X = a.toJSON()
        Y = self.inputY
        self.assertDictEqual(X, Y, "Loading and dumping to JSON does not " + \
                             " work: " + str(X) + " != " + str(Y))
    
            
    def test_state(self):
        for numType in self.mathTypes:
            state = GeneralizedState(numType)
            state.load(self.inputY)
            #test duration
            X = list(state.durationGenerator())
            Y = [(1, numType(0.5)), (2, numType(0.5))]
            self.assertEqual(X, Y, "HMM.durationGenerator() does not work: " + \
                             str(X) + " != " + str(Y))
            #test emission
            Y = numType(0.5)
            X = state.emission("000", 1, 1)
            self.assertAlmostEqual(X, Y, delta=1e-7, 
                                   msg="HMM.emission(\"000\", 1, 1) does not " \
                                   + "work: " + str(X) + " != " + str(Y))
            Y = numType(0.5)
            X = state.emission("000", 1, 2)
            self.assertAlmostEqual(X, Y, delta=1e-7, 
                                   msg="HMM.emission(\"000\", 1, 2) does not " \
                                   + "work: " + str(X) + " != " + str(Y))
             
             
    def test_forward(self):
        for mathType in self.mathTypes:
            sequence = "000000"
            sequenceLength = len(sequence)
            hmm = self.HMM[mathType]
            X = hmm.getForwardTable(sequence, 0, sequenceLength)
            Y =  [
                (0, [{1: 0.2}, {1: 0.8}]),
                (1, [{1: 0.23}, {1: 0.27}]),
                (2, [{1: 0.102, 2: 0.23}, {1: 0.148, 2: 0.27}]),
                (3, [{1: 0.1543, 2: 0.102}, {1: 0.2207, 2: 0.148}]),
                (4, [{1: 0.13062, 2: 0.1543}, {1: 0.18188, 2: 0.2207}]),
                (5, [{1: 0.143383, 2: 0.13062}, {1: 0.200367, 2: 0.18188}]),
                (6, [{1: 0.1366622, 2: 0.143383}, {1: 0.1914628, 2: 0.200367}]),
            ]
            self.assertEqual(len(X), len(Y), 
                             "Output from forward has wrong length.")
            for i in range(len(X)):
                self.assertEqual(len(X[i]), len(Y[i]), 
                                 "Output from forward has wrong length.")
                Xi = X[i][0]
                Yi = Y[i][0]
                XX = X[i][1]
                YY = Y[i][1]
                self.assertEqual(Xi, Yi, 
                                 "Output from forward have wrong indices.")
                self.assertEqual(len(XX), len(YY), 
                                 "Output from forward have wrong length.")
                for j in range(len(XX)):
                    self.assertEqual(len(XX[j]), len(YY[j]), 
                                     "Dictionary has wrong length.")
                    for (key, value) in XX[j].iteritems():
                        if key not in YY[j]:
                            self.fail("Key missing in dictionary")
                        self.assertAlmostEqual(float(value), float(YY[j][key]), 
                                               delta=1e-7, 
                                               msg="Dict has wrong value.")
         
    
    def test_backward(self):
        for mathType in self.mathTypes:
            sequence = "000000"
            sequenceLength = len(sequence)
            hmm = self.HMM[mathType]
            X = hmm.getBackwardTable(sequence, 0, sequenceLength)
            Y = [
                (6, [{1: 1.0}, {1: 1.0}]),
                (5, [{1: 0.5}, {1: 0.5}]),
                (4, [{1: 0.25, 2: 0.5}, {1: 0.25, 2: 0.5}]),
                (3, [{1: 0.375, 2: 0.25}, {1: 0.375, 2: 0.25}]),
                (2, [{1: 0.3125, 2: 0.375}, {1: 0.3125, 2: 0.375}]),
                (1, [{1: 0.34375, 2: 0.3125}, {1: 0.34375, 2: 0.3125}]),
                (0, [{1: 0.328125, 2: 0.34375}, {1: 0.328125, 2: 0.34375}]),
            ]
            self.assertEqual(len(X), len(Y), 
                             "Output from backward has wrong length.")
            for i in range(len(X)):
                self.assertEqual(len(X[i]), len(Y[i]), 
                                 "Output from backward has wrong length.")
                Xi = X[i][0]
                Yi = Y[i][0]
                XX = X[i][1]
                YY = Y[i][1]
                self.assertEqual(Xi, Yi, 
                                 "Output from backward have wrong indices.")
                self.assertEqual(len(XX), len(YY), 
                                 "Output from backward have wrong length.")
                for j in range(len(XX)):
                    self.assertEqual(len(XX[j]), len(YY[j]), 
                                     "Dictionary has wrong length.")
                    for (key, value) in XX[j].iteritems():
                        if key not in YY[j]:
                            self.fail("Key missing in dictionary")
                        self.assertAlmostEqual(float(value), float(YY[j][key]), 
                                               delta=1e-7, 
                                               msg="Dict has wrong value.")
    
    
    
if __name__ == '__main__':
    unittest.main()