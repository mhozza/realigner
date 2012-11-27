#TODO: najskor otestuj zvysny kod a az potom pis novy
from HMM import State

import SpecialHMMs

  

class RepeatProfileFactory:
            
    def __init__(self, mathType=float):
        self.a = 2
        self.cache = dict()
        self.mathType = mathType
        
    def getHMM(self, consensus):
        if consensus in self.cache:
            return self.cache[consensus]
        self.cache[consensus] = SpecialHMMs.createProfileHMM(self.mathType, 
            consensus, 23.0, 
            [("A", 0.25), ("C", 0.25), ("G", 0.25), ("T", 0.25)], {})
        return self.cache[consensus]
        
    
    

class PairRepeatState(State):
    
    def __init__(self, *p):
        State.__init__(self, *p)
        self.hmm = None
        self.factory = RepeatProfileFactory()
        
    def load(self, dictionary):
        State.load(self, dictionary)
        
    
    def durationGenerator(self):
        for i in range(1,10000):
            for j in range(0,i):
                yield(((j,i-j),0.001)) # now for some trivial distribution
        
        
    def emission(self, X, x, dx, Y, y, dy, consensus):
        hmm = self.factory.getHMM(consensus)
        return \
            hmm.getProbability(X, x, dx) * \
            hmm.getProbobility(Y, y, dy)
        