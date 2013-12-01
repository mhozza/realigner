from hack.PairClassifier import PairClassifier
from hack.AnnotationLoader import AnnotationLoader
from hmm.PairHMM import GeneralizedPairState
import sys
from hack.DataPreparer import DataPreparer


class ClassifierState(GeneralizedPairState):
    def __init__(self, *p):
        GeneralizedPairState.__init__(self, *p)
        self.dp = DataPreparer()
        self.clf = PairClassifier(self.dp)
        self.al = AnnotationLoader()
        self.annotations, self.aX, self.aY = self.al.get_annotations("data/sequences/simulated_alignment.js")

    def emission(self, X, x, dx, Y, y, dy):
        #if(dx!=1 && dy!=1) throw Some Exception

        if x >= len(X) or y >= len(Y):
            sys.stderr.write("WARNING: index out of bounds\n")
            return 0

        return self.clf.prepare_predict(X, x, self.aX, Y, y, self.aY)


class SimpleState(GeneralizedPairState):
    def emission(self, X, x, dx, Y, y, dy):
        return 1
