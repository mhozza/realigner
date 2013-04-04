from tools.ConfigFactory import ConfigFactory
from hmm.HMM import HMM, State
from hmm.GeneralizedHMM import GeneralizedHMM, GeneralizedState
from hmm.PairHMM import GeneralizedPairHMM, GeneralizedPairState
from repeats.RepeatAlignmentState import PairRepeatState
from hmm.SpecialHMMs import JukesCantorGenerator, \
                               BackgroundProbabilityGenerator
from repeats.RepeatLengthDistribution import RepeatLengthDistribution
from repeats.HighOrderRepeatState import HighOrderRepeatState
from hmm.HighOrderState import HighOrderState
import json
from hack.ClassifierState import ClassifierState, SimpleState
from algorithm.LogNum import LogNum

def getInitializerObject(tp, mathType):
    def __getInitializer(dictionary):
        t = tp(mathType)
        t.load(dictionary)
        return t
    return __getInitializer


def getInitializerFunction(function, mathType):
    def __getInitializer(dictionary):
        return function(dictionary, mathType)
    return __getInitializer


class HMMLoader(ConfigFactory):
    
    def __init__(self, mathType=float):
        ConfigFactory.__init__(self)
        self.mathType=mathType
        for obj in [
            HMM, 
            State, 
            GeneralizedHMM, 
            GeneralizedState, 
            GeneralizedPairHMM, 
            GeneralizedPairState,
            PairRepeatState,
			ClassifierState,
            HighOrderState,
            HighOrderRepeatState,
            RepeatLengthDistribution,
            SimpleState,
			LogNum,
        ]:

            self.addFunction(obj.__name__, getInitializerObject(obj, mathType))
        
        for (name, function) in [
            ("JukesCantorGenerator", JukesCantorGenerator),
            ("backgroundprob", BackgroundProbabilityGenerator),
        ]:
            self.addFunction(name, getInitializerFunction(function, mathType))
        
        for (name, constant) in [
            # STUB 
        ]:
            self.addConstant(name, constant)

            
if __name__ == "__main__":
    a = HMMLoader()
    try:
        rr = a.load("test_data/sampleHMM.js")
    except str as e:
        print(e)
    for r in rr:
        print r
        print r.toJSON()
        print(json.dumps(r.toJSON(), sort_keys = True))