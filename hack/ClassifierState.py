from hmm.GeneralizedHMM import GeneralizedState
from sklearn.ensemble import RandomForestRegressor


class RandomForestDtate(GeneralizedState):
    def __init__(self):
        self.clf = RandomForestRegressor(n_estimators=111, min_samples_split=1, random_state=1)
        #clf.set_params()
    
    def train(self, data):
        self.clf.fit(data.data, data.target)
        #save state to file
        
#    def load(self, dictionary):
#        GeneralizedState.load(self, dictionary)        
#    
#    def durationGenerator(self, _, __):
#        return GeneralizedState.durationGenerator(self)
#    
#
#    def reverseDurationGenerator(self, _, __):
#        return GeneralizedState.durationGenerator(self)
    
        
    def emission(self, X, x, dx, Y, y, dy):
        #if(dx!=1 && dy!=1) throw Some Exception 
        return self.clf.predict([X[x], Y[y]])
    
    
#    def buildSampleEmission(self):
#        duration_dict = defaultdict(float)
#        for (k, v) in self.durations:
#            duration_dict[k] += v
#        em = dict(self.emissions)
#        for (key, _) in em.iteritems():
#            em[key] *= duration_dict[(len(key[0]), len(key[1]))]
#        self._sampleEmission = rand_generator(em)
         
