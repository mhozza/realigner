from hmm.GeneralizedHMM import GeneralizedState
from ClassifierDemo import AnnotatedBaseCouple


class RandomForestState(GeneralizedState):
    def __init__(self, clf):
        self.clf = clf            
      
    def emission(self, X, x, dx, Y, y, dy):
        #if(dx!=1 && dy!=1) throw Some Exception 
        xy = AnnotatedBaseCouple()
        xy.X.base = X[x]
        xy.Y.base = Y[y]        
#        todo annotations
        return self.clf.predict(xy)
