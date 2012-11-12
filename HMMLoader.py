from ConfigFactory import ConfigFactory
from HMM import HMM, State
from GeneralizedHMM import GeneralizedHMM, GeneralizedState
from PairHMM import GeneralizedPairHMM, GeneralizedPairState
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
            GeneralizedPairState
        ]:

            print (obj.__name__ + " added")
            self.addObject(obj)

            
if __name__ == "__main__":
    a = HMMLoader()
    try:
        rr = a.load("test_data/sampleHMM.js")
    except str as e:
        print(e)
    for r in rr:
        print r
        print(json.dumps(r.toJSON(), sort_keys=True, indent=4))
    