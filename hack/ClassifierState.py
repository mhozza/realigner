from hmm.PairHMM import GeneralizedPairState
from hack.PairClassifier import PairClassifier, DataLoader, AnnotatedBaseCouple, AnnotatedBase


class ClassifierState(GeneralizedPairState):
    def __init__(self, *p):
        GeneralizedPairState.__init__(self, *p)
        self.clf = PairClassifier()
        self.dl = DataLoader()
        self.aX, self.aY = self.dl.getAnnotations("data/sequences/annotations/simulated_alignment.fa")
        
        
      
    def emission(self, X, x, dx, Y, y, dy):
        #if(dx!=1 && dy!=1) throw Some Exception 
        xy = AnnotatedBaseCouple()
        xy.X.base = X[x]
        xy.Y.base = Y[y] 
        xy.X.annotations = self.dl.getAnnotationsAt(self.aX, x)       
        xy.Y.annotations = self.dl.getAnnotationsAt(self.aY, y)
#        todo annotations
        return self.clf.predict(xy.toTrainData(AnnotatedBase(), AnnotatedBase()))
