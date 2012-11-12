#TODO: najskor otestuj zvysny kod a az potom pis novy

from HMM import State

class PairRepeatState(State):
    
    def __init__(self, *p):
        State.__init__(self, *p)
        self.hmm = None
        
    def load(self, dictionary):
        State.load(self, dictionary)
        
    
    def durationGenerator(self):
        for i in range(1,10000):
            for j in range(0,i):
                yield(((j,i-j),0.001)) # now for some trivial distribution
        
        
    def emission(self, X, Y, x, y, dx, dy):
        #TODO: cachovanie hodnot, memoizacia, skonstruovanie 
        return \
            self.hmm.getProbability(X, x, dx) * \
            self.hmm.getProbobility(Y, y, dy)
        # vyrobime HMM, vypocitame hodnotu a zacachujeme ju, lebo ju budeme 
        # mozno neskor znova potrebovat
        # TODO: pridaj aj hashovanie a memoizaciu, nech nekonstruujem tie iste 
        # objekty viac krat -- na to by sa mozno hodila nejaka factory       
        