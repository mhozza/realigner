from tools.ConfigFactory import ConfigFactory
from hmm.HMM import HMM, State
from hmm.GeneralizedHMM import GeneralizedHMM, GeneralizedState
from hmm.PairHMM import GeneralizedPairHMM, GeneralizedPairState
from models.RepeatAlignmentState import PairRepeatState
from models.SpecialHMMs import JukesCantorGenerator, \
                               BackgroundProbabilityGenerator
import json

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
        ]:

            print (obj.__name__ + " added")
            self.addFunction(obj.__name__, getInitializerObject(obj, mathType))
        
        for (name, function) in [
            ("JukesCantorGenerator", JukesCantorGenerator),
            ("backgroundprob", BackgroundProbabilityGenerator),
        ]:
            print (function.__name__ + " added under name " + name)
            self.addFunction(name, getInitializerFunction(function, mathType))
        
        for (name, constant) in [
            # STUB 
        ]:
            print (str(constant) + " added under name " + name)
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