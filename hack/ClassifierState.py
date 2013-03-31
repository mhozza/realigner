from hmm.PairHMM import GeneralizedPairState
from PairClassifier import AnnotatedBaseCouple
from hack.PairClassifier import PairClassifier


class ClassifierState(GeneralizedPairState):
    def __init__(self, *p):
        GeneralizedPairState.__init__(self, *p)
        self.clf = PairClassifier()           
      
    def emission(self, X, x, dx, Y, y, dy):
        #if(dx!=1 && dy!=1) throw Some Exception 
        xy = AnnotatedBaseCouple()
        xy.X.base = X[x]
        xy.Y.base = Y[y]        
#        todo annotations
        return self.clf.predict(xy)
