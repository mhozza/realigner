from hack.PairClassifier import PairClassifier
import hack.DataLoader
from hmm.PairHMM import GeneralizedPairState
import sys


class ClassifierState(GeneralizedPairState):
    def __init__(self, *p):
        GeneralizedPairState.__init__(self, *p)
        self.clf = PairClassifier()
        self.dl = hack.DataLoader.DataLoader()
        self.annotations, self.aX, self.aY = self.dl.getAnnotations("data/sequences/simulated_alignment.js")

    def emission(self, X, x, dx, Y, y, dy):
        #if(dx!=1 && dy!=1) throw Some Exception
        xy = hack.DataLoader.AnnotatedBaseCouple()
        if x>=len(X) or y>=len(Y):
            sys.stderr.write("WARNING: index out of bounds\n")
            return 0
        xy.X.base = X[x]
        xy.Y.base = Y[y]
        xy.X.annotations = self.dl.getAnnotationsAt(self.aX, x)
        xy.Y.annotations = self.dl.getAnnotationsAt(self.aY, y)
        return self.clf.predict(xy.toTrainData())


class SimpleState(GeneralizedPairState):
    def emission(self, X, x, dx, Y, y, dy):
        return 1
