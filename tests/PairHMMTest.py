import unittest
from PairHMM import GeneralizedPairState, GeneralizedPairHMM

class ConfigFactoryTest(unittest.TestCase):
    
            
    def __init__(self, *p):
        unittest.TestCase.__init__(self, *p)
        self.Y = None
        self.inputY = None
        self.mathTypes = [float]#, LogNum]
        
    
    def setUp(self):
        self.inputY = {
            "__name__": "GeneralizedPairState",
            "name": "name",
            "startprob": 1.0,
            "emission": [(("0", "0"), 1.0), (("00", ""), 1.0)],
            "endprob": 0.5,
            "durations": [((1, 1), 0.5), ((2, 0), 0.5)]
        } 
        self.HMM = dict()
        
        for mathType in self.mathTypes:
             
            hmmInit = {
                "__name__": "GeneralizedPairHMM",
                "states": [],
                "transitions": [
                    {"from": "one", "to": "one", "prob": mathType(0.3)},
                    {"from": "one", "to": "two", "prob": mathType(0.6)},
                    {"from": "one", "to": "three", "prob": mathType(0.1)},
                    {"from": "two", "to": "one", "prob": mathType(0.5)},
                    {"from": "two", "to": "two", "prob": mathType(0.4)},
                    {"from": "two", "to": "three", "prob": mathType(0.1)},
                    {"from": "three", "to": "one", "prob": mathType(0.2)},
                    {"from": "three", "to": "two", "prob": mathType(0.3)},
                    {"from": "three", "to": "three", "prob": mathType(0.5)},
                ]
            }
            one = GeneralizedPairState(mathType)
            one.load({
                "__name__": "GeneralizedPairState",
                "name": "one",
                "startprob": 0.2,
                "endprob": 1.0,
                "emission": [(("0", "0"), 1.0), (("00", "00"), 1.0)],
                "durations": [((1, 1), 0.5), ((2, 2), 0.5)]
            })
            two = GeneralizedPairState(mathType)
            two.load({
                "__name__": "GeneralizedPairState",
                "name": "two",
                "startprob": 0.8,
                "endprob": 1.0,
                "emission": [(("0", ""), 1.0), (("00", "0"), 1.0)],
                "durations": [((1, 0), 0.5), ((2, 1), 0.5)]
            })
            three = GeneralizedPairState(mathType)
            three.load({
                "__name__": "GeneralizedPairState",
                "name": "three",
                "startprob": 0.8,
                "endprob": 1.0,
                "emission": [(("", "0"), 1.0), (("0", "00"), 1.0)],
                "durations": [((0, 1), 0.5), ((1, 2), 0.5)]
            }) 
            hmmInit["states"] = [one, two, three]
            self.HMM[mathType] = GeneralizedPairHMM(mathType)
            self.HMM[mathType].load(hmmInit)
        
            
    def test_state_loading(self):
        a = GeneralizedPairState()
        a.load(self.inputY)
        X = a.toJSON()
        Y = self.inputY
        X['emission'].sort()
        Y['emission'].sort()
        X['durations'].sort()
        Y['durations'].sort()
        self.assertDictEqual(X, Y, "Loading and dumping to JSON does not " + \
                             " work: \n" + str(X) + " != \n" + str(Y))
    
            
    def test_state(self):
        for numType in self.mathTypes:
            state = GeneralizedPairState(numType)
            state.load(self.inputY)
            #test duration
            X = list(state.durationGenerator())
            Y = [((1, 1), numType(0.5)), ((2, 0), numType(0.5))]
            self.assertEqual(X, Y, "HMM.durationGenerator() does not work: " + \
                             str(X) + " != " + str(Y))
            #test emission
            Y = numType(1.0)
            X = state.emission("000", 1, 1, "000", 2, 1)
            self.assertAlmostEqual(X, Y, delta=1e-7, 
                                   msg="HMM.emission(\"000\", 1, 1) does not " \
                                   + "work: " + str(X) + " != " + str(Y))
            Y = numType(1.0)
            X = state.emission("000", 1, 2, "000000", 2, 0)
            self.assertAlmostEqual(X, Y, delta=1e-7, 
                                   msg="HMM.emission(\"000\", 1, 2) does not " \
                                   + "work: " + str(X) + " != " + str(Y))
             
             
    def test_forward(self):
        for mathType in self.mathTypes:
            sequenceA = "000000"
            sequenceB = "000"
            sequenceALength = len(sequenceA)
            sequenceBLength = len(sequenceB)
            hmm = self.HMM[mathType]
            X = hmm.getForwardTable(sequenceA, 0, sequenceALength,
                                    sequenceB, 0, sequenceBLength)
           
          
            Y = [
                (0, {
                    0: {
                        0: {(0, 0): 0.2},
                        1: {(0, 0): 0.8},
                        2: {(0, 0): 0.8}
                    },
                    1: {
                        0: {},
                        1: {},
                        2: {(0, 1): 0.25}
                    },
                    2: {
                        0: {},
                        1: {},
                        2: {(0, 1): 0.0625}
                    },
                    3: {
                        0: {},
                        1: {},
                        2: {(0, 1): 0.015625}
                    }
                }),
                (1, {
                    0: {
                        0: {},
                        1: {(1, 0): 0.34},
                        2: {}
                    },
                    1: {
                        0: {(1, 1): 0.31},
                        1: {(1, 0): 0.0375},
                        2: {(0, 1): 0.017}
                    },
                    2: {
                        0: {(1, 1): 0.025},
                        1: {(1, 0): 0.009375},
                        2: {(1, 2): 0.25, (0, 1): 0.021625}
                    },
                    3: {
                        0: {(1, 1): 0.00625},
                        1: {(1, 0): 0.00234375},
                        2: {(1, 2): 0.0625, (0, 1): 0.069625}
                    }
                }),
                (2, {
                    0: {
                        0: {},
                        1: {(1, 0): 0.068},
                        2: {}
                    },
                    1: {
                        0: {(1, 1): 0.085},
                        1: {(1, 0): 0.10305, (2, 1): 0.34},
                        2: {(0, 1): 0.0034}
                    },
                    2: {
                        0: {(1, 1): 0.057575, (2, 2): 0.31},
                        1: {(1, 0): 0.05011875, (2, 1): 0.0375},
                        2: {(1, 2): 0.017, (0, 1): 0.0272525}
                    },
                    3: {
                        0: {(1, 1): 0.03325625, (2, 2): 0.025},
                        1: {(1, 0): 0.0221625, (2, 1): 0.009375},
                        2: {(1, 2): 0.021625, (0, 1): 0.0338228125}
                    }
                }),
                (3, {
                    0: {
                        0: {},
                        1: {(1, 0): 0.0136},
                        2: {}
                    },
                    1: {
                        0: {(1, 1): 0.017},
                        1: {(1, 0): 0.11462, (2, 1): 0.068},
                        2: {(0, 1): 0.00068}
                    },
                    2: {
                        0: {(1, 1): 0.1238525, (2, 2): 0.085},
                        1: {(1, 0): 0.134434125, (2, 1): 0.10305},
                        2: {(1, 2): 0.0034, (0, 1): 0.010151}
                    },
                    3: {
                        0: {(1, 1): 0.0814661875, (2, 2): 0.057575},
                        1: {(1, 0): 0.032101546875, (2, 1): 0.05011875},
                        2: {(1, 2): 0.0272525, (0, 1): 0.02570458125}
                    }
                }),
                (4, {
                    0: {
                        0: {},
                        1: {(1, 0): 0.00272},
                        2: {}
                    },
                    1: {
                        0: {(1, 1): 0.0034},
                        1: {(1, 0): 0.041726, (2, 1): 0.0136},
                        2: {(0, 1): 0.000136}
                    },
                    2: {
                        0: {(1, 1): 0.048273, (2, 2): 0.017},
                        1: {(1, 0): 0.112185225, (2, 1): 0.11462},
                        2: {(1, 2): 0.00068, (0, 1): 0.0029703}
                    },
                    3: {
                        0: {(1, 1): 0.09205400625, (2, 2): 0.1238525},
                        1: {(1, 0): 0.0660999778125, (2, 1): 0.134434125},
                        2: {(1, 2): 0.010151, (0, 1): 0.01551648625}
                    }
                }),
                (5, {
                    0: {
                        0: {},
                        1: {(1, 0): 0.000544},
                        2: {}
                    },
                    1: {
                        0: {(1, 1): 0.00068},
                        1: {(1, 0): 0.0121056, (2, 1): 0.00272},
                        2: {(0, 1): 2.72e-05}
                    },
                    2: {
                        0: {(1, 1): 0.0143551, (2, 2): 0.0034},
                        1: {(1, 0): 0.06549049, (2, 1): 0.041726},
                        2: {(1, 2): 0.000136, (0, 1): 0.00078208}
                    },
                    3: {
                        0: {(1, 1): 0.06685728625, (2, 2): 0.048273},
                        1: {(1, 0): 0.108728895375, (2, 1): 0.112185225},
                        2: {(1, 2): 0.0029703, (0, 1): 0.0064780995}
                    }
                }),
                (6, {
                    0: {
                        0: {},
                        1: {(1, 0): 0.0001088},
                        2: {}
                    },
                    1: {
                        0: {(1, 1): 0.000136},
                        1: {(1, 0): 0.0031732, (2, 1): 0.000544},
                        2: {(0, 1): 5.44e-06}
                    },
                    2: {
                        0: {(1, 1): 0.00381112, (2, 2): 0.00068},
                        1: {(1, 0): 0.02690754, (2, 1): 0.0121056},
                        2: {(1, 2): 2.72e-05, (0, 1): 0.00019402}
                    },
                    3: {
                        0: {(1, 1): 0.0295591955, (2, 2): 0.0143551},
                        1: {(1, 0): 0.080139169875, (2, 1): 0.06549049},
                        2: {(1, 2): 0.00078208, (0, 1): 0.002230518}
                    }
                }),
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
                            
                        for (kk, vv) in value.iteritems():
                            if kk not in YY[j][key]:
                                self.fail("Key missing in dictionary.")
                            self.assertAlmostEqual(float(vv), 
                                                   float(YY[j][key][kk]), 
                                                   delta=1e-7, 
                                                   msg="Dict has wrong value.")
         
    
    def test_backward(self):
        for mathType in self.mathTypes:
            sequenceA = "000000"
            sequenceB = "000"
            sequenceALength = len(sequenceA)
            sequenceBLength = len(sequenceB)
            hmm = self.HMM[mathType]
            X = hmm.getBackwardTable(sequenceA, 0, sequenceALength,
                                     sequenceB, 0, sequenceBLength)
            Y = [
                (6, {
                    0: {
                        0: {},
                        1: {},
                        2: {(0, 1): 0.03125}
                    },
                    1: {
                        0: {},
                        1: {},
                        2: {(0, 1): 0.125}
                    },
                    2: {
                        0: {},
                        1: {},
                        2: {(0, 1): 0.5}
                    },
                    3: {
                        0: {(0, 0): 1.0},
                        1: {(0, 0): 1.0},
                        2: {(0, 0): 1.0}
                    }
                }),
                (5, {
                    0: {
                        0: {(1, 1): 0.00625},
                        1: {(1, 0): 0.0015625},
                        2: {(1, 2): 0.125, (0, 1): 0.1465625}
                    },
                    1: {
                        0: {(1, 1): 0.025},
                        1: {(1, 0): 0.00625},
                        2: {(1, 2): 0.5, (0, 1): 0.0725}
                    },
                    2: {
                        0: {(1, 1): 0.5},
                        1: {(1, 0): 0.025},
                        2: {(0, 1): 0.075}
                    },
                    3: {
                        0: {},
                        1: {(1, 0): 0.5},
                        2: {}
                    }
                }),
                (4, {
                    0: {
                        0: {(1, 1): 0.03425, (2, 2): 0.025},
                        1: {(1, 0): 0.015453125, (2, 1): 0.00625},
                        2: {(1, 2): 0.0725, (0, 1): 0.114996875}
                    },
                    1: {
                        0: {(1, 1): 0.08625, (2, 2): 0.5},
                        1: {(1, 0): 0.036125, (2, 1): 0.025},
                        2: {(1, 2): 0.075, (0, 1): 0.1138125}
                    },
                    2: {
                        0: {(1, 1): 0.15},
                        1: {(1, 0): 0.13375, (2, 1): 0.5},
                        2: {(0, 1): 0.015}
                    },
                    3: {
                        0: {},
                        1: {(1, 0): 0.1},
                        2: {}
                    }
                }),
                (3, {
                    0: {
                        0: {(1, 1): 0.115715625, (2, 2): 0.08625},
                        1: {(1, 0): 0.02852796875, (2, 1): 0.036125},
                        2: {(1, 2): 0.1138125, (0, 1): 0.09625921875}
                    },
                    1: {
                        0: {(1, 1): 0.213375, (2, 2): 0.15},
                        1: {(1, 0): 0.168228125, (2, 1): 0.13375},
                        2: {(1, 2): 0.015, (0, 1): 0.0435}
                    },
                    2: {
                        0: {(1, 1): 0.03},
                        1: {(1, 0): 0.165, (2, 1): 0.1},
                        2: {(0, 1): 0.003}
                    },
                    3: {
                        0: {},
                        1: {(1, 0): 0.02},
                        2: {}
                    }
                }),
                (2, {
                    0: {
                        0: {(1, 1): 0.1480246875, (2, 2): 0.213375},
                        1: {(1, 0): 0.0739255859375, (2, 1): 0.168228125},
                        2: {(1, 2): 0.0435, (0, 1): 0.06325153125}
                    },
                    1: {
                        0: {(1, 1): 0.08415, (2, 2): 0.03},
                        1: {(1, 0): 0.154164375, (2, 1): 0.165},
                        2: {(1, 2): 0.003, (0, 1): 0.0128475}
                    },
                    2: {
                        0: {(1, 1): 0.006},
                        1: {(1, 0): 0.06065, (2, 1): 0.02},
                        2: {(0, 1): 0.0006}
                    },
                    3: {
                        0: {},
                        1: {(1, 0): 0.004},
                        2: {}
                    }
                }),
                (1, {
                    0: {
                        0: {(1, 1): 0.1136641875, (2, 2): 0.08415},
                        1: {(1, 0): 0.144118240625, (2, 1): 0.154164375},
                        2: {(1, 2): 0.0128475, (0, 1): 0.0271841625}
                    },
                    1: {
                        0: {(1, 1): 0.025125, (2, 2): 0.006},
                        1: {(1, 0): 0.09316275, (2, 1): 0.06065},
                        2: {(1, 2): 0.0006, (0, 1): 0.003399}
                    },
                    2: {
                        0: {(1, 1): 0.0012},
                        1: {(1, 0): 0.01766, (2, 1): 0.004},
                        2: {(0, 1): 0.00012}
                    },
                    3: {
                        0: {},
                        1: {(1, 0): 0.0008},
                        2: {}
                    }
                }),
                (0, {
                    0: {
                        0: {(1, 1): 0.051012525, (2, 2): 0.025125},
                        1: {(1, 0): 0.111111653125, (2, 1): 0.09316275},
                        2: {(1, 2): 0.003399, (0, 1): 0.0094903875}
                    },
                    1: {
                        0: {(1, 1): 0.006684, (2, 2): 0.0012},
                        1: {(1, 0): 0.03874375, (2, 1): 0.01766},
                        2: {(1, 2): 0.00012, (0, 1): 0.0008457}
                    },
                    2: {
                        0: {(1, 1): 0.00024},
                        1: {(1, 0): 0.004638, (2, 1): 0.0008},
                        2: {(0, 1): 2.4e-05}
                    },
                    3: {
                        0: {},
                        1: {(1, 0): 0.00016},
                        2: {}
                    }
                }),
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
                        for (kk, vv) in value.iteritems():
                            if kk not in YY[j][key]:
                                self.fail("Key missing in dictionary.")
                            self.assertAlmostEqual(float(vv), 
                                                   float(YY[j][key][kk]), 
                                                   delta=1e-7, 
                                                   msg="Dict has wrong value.")
    
    def test_posterior(self):   
        for mathType in self.mathTypes:
            sequenceA = "000000"
            sequenceB = "000"
            sequenceALength = len(sequenceA)
            sequenceBLength = len(sequenceB)
            hmm = self.HMM[mathType]
            X = hmm.getPosteriorTable(sequenceA, 0, sequenceALength,
                                      sequenceB, 0, sequenceBLength)
            Y = [
                {
                    0: {(1, 0, 0): 0.09685397, (0, 0, 0): 0.029338967625, (2, 0, 0): 0.06636361575}, 
                    1: {(2, 0, 1): 0.00474519375}, 
                    2: {(2, 0, 1): 0.0001057125}, 
                    3: {(2, 0, 1): 7.5e-07}, 
                },
                {
                    0: {(1, 1, 0): 0.075555924125}, 
                    1: {(0, 1, 1): 0.0316277655, (2, 0, 1): 0.000924261525, (1, 1, 0): 0.00290578125}, 
                    2: {(0, 1, 1): 0.0003342, (2, 0, 1): 0.00014700675, (2, 1, 2): 0.0016995, (1, 1, 0): 8.69625e-05}, 
                    3: {(0, 1, 1): 3e-06, (2, 0, 1): 1.671e-05, (2, 1, 2): 1.5e-05, (1, 1, 0): 7.5e-07}, 
                },
                {
                    0: {(1, 1, 0): 0.019600080725}, 
                    1: {(0, 1, 1): 0.019322911875, (2, 0, 1): 0.0004301104125, (1, 2, 1): 0.06335067, (1, 1, 0): 0.019200842775}, 
                    2: {(0, 1, 1): 0.00289314375, (2, 1, 2): 0.000436815, (1, 1, 0): 0.00177019425, (1, 2, 1): 0.0013245, (0, 2, 2): 0.0155775, (2, 0, 1): 0.0007002529875}, 
                    3: {(0, 1, 1): 7.9815e-05, (2, 1, 2): 2.595e-05, (1, 1, 0): 3.546e-05, (1, 2, 1): 1.5e-05, (0, 2, 2): 6e-05, (2, 0, 1): 4.0587375e-05}, 
                },
                {
                    0: {(1, 1, 0): 0.0020107759375}, 
                    1: {(0, 1, 1): 0.005032839375, (2, 0, 1): 0.0001309125375, (1, 2, 1): 0.020966355, (1, 1, 0): 0.035340641325}, 
                    2: {(0, 1, 1): 0.02084437575, (2, 1, 2): 0.0002958, (1, 1, 0): 0.0163068593625, (1, 2, 1): 0.012499965, (0, 2, 2): 0.0143055, (2, 0, 1): 0.000883137}, 
                    3: {(0, 1, 1): 0.00097759425, (2, 1, 2): 0.000163515, (1, 1, 0): 0.000256812375, (1, 2, 1): 0.00040095, (0, 2, 2): 0.0006909, (2, 0, 1): 0.0001542274875}, 
                },
                {
                    0: {(1, 1, 0): 0.00015519215}, 
                    1: {(0, 1, 1): 0.00078686625, (2, 0, 1): 3.127915e-05, (1, 2, 1): 0.004575805, (1, 1, 0): 0.0140389734875}, 
                    2: {(0, 1, 1): 0.02060050275, (2, 1, 2): 0.000154785, (1, 1, 0): 0.03702112425, (1, 2, 1): 0.0378246, (0, 2, 2): 0.00725475, (2, 0, 1): 0.0006761145375}, 
                    3: {(0, 1, 1): 0.005523240375, (2, 1, 2): 0.00030453, (1, 1, 0): 0.0026439991125, (1, 2, 1): 0.005377365, (0, 2, 2): 0.00743115, (2, 0, 1): 0.0004654945875}, 
                },
                {
                    0: {(1, 1, 0): 1.6813e-05}, 
                    1: {(0, 1, 1): 4.658e-05, (2, 0, 1): 7.973e-06, (1, 2, 1): 0.00019652, (1, 1, 0): 0.0008746296}, 
                    2: {(0, 1, 1): 0.00247625475, (2, 1, 2): 1.972e-05, (1, 1, 0): 0.017518706075, (1, 2, 1): 0.011161705, (0, 2, 2): 0.0005865, (2, 0, 1): 0.0001134016}, 
                    3: {(0, 1, 1): 0.020057185875, (2, 1, 2): 0.000445545, (1, 1, 0): 0.021745779075, (1, 2, 1): 0.022437045, (0, 2, 2): 0.0144819, (2, 0, 1): 0.000971714925}, 
                },
                {
                    0: {(1, 1, 0): 3.4e-07}, 
                    1: {(0, 1, 1): 1.7e-06, (2, 0, 1): 3.4e-07, (1, 2, 1): 6.8e-06, (1, 1, 0): 3.9665e-05}, 
                    2: {(0, 1, 1): 0.000190556, (2, 1, 2): 6.8e-06, (1, 1, 0): 0.001345377, (1, 2, 1): 0.00060528, (0, 2, 2): 3.4e-05, (2, 0, 1): 4.8505e-05}, 
                    3: {(0, 1, 1): 0.0295591955, (2, 1, 2): 0.00078208, (1, 1, 0): 0.080139169875, (1, 2, 1): 0.06549049, (0, 2, 2): 0.0143551, (2, 0, 1): 0.002230518}, 
                },
            ]
            self.assertEqual(len(X), len(Y), 
                             "Output from posterior has wrong length.")
            for i in range(len(X)):
                self.assertEqual(len(X[i]), len(Y[i]), 
                                 "Output from posterior has wrong length.")
                XX = X[i]
                YY = Y[i]
                self.assertEqual(len(XX), len(YY), 
                                 "Output from posterior have wrong length.")
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