from ConfigFactory import ConfigFactory
from HMM import HMM, State
from GeneralizedHMM import GeneralizedHMM, GeneralizedState
from PairHMM import GeneralizedPairHMM, GeneralizedPairState
from RepeatAlignmentState import PairRepeatState
from SpecialHMMs import JukesCantorGenerator, BackgroundProbabilityGenerator
import json

class HMMLoader(ConfigFactory):
    
    def __init__(self):
        ConfigFactory.__init__(self)
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
            self.addObject(obj)
        
        for (name, function) in [
            ("JukesCantorGenerator", JukesCantorGenerator),
            ("backgroundprob", BackgroundProbabilityGenerator),
        ]:
            print (function.__name__ + " added under name " + name)
            self.addFunction(name, function)
        
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