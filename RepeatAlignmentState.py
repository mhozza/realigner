class PairRepeatState(GeneralizedPairState):
    
    def __init__(self):
        return
    
    def durationGenerator(self):
        for i in range(1,10000):
            for j in range(0,i):
                yield(((j,i-j),0.001)) # now for some trivial distribution
        
    def emission(self, X, Y, x, y, dx, dy):
        self.hmm.getProbability(X, Y, x, y, dx, dy)
        # vyrobime HMM, vypocitame hodnotu a zacachujeme ju, lebo ju budeme 
        # mozno neskor znova potrebovat
        # TODO: pridaj aj hashovanie a memoizaciu, nech nekonstruujem tie iste 
        # objekty viac krat -- na to by sa mozno hodila nejaka factory       
        
