from hack.PairClassifier import PairClassifier
from hack.AnnotationLoader import AnnotationLoader
from hmm.PairHMM import GeneralizedPairState
import sys
from hack.DataPreparer import DataPreparer


class ClassifierState(GeneralizedPairState):
    def __init__(self, *p):
        GeneralizedPairState.__init__(self, *p)
        self.dp = DataPreparer(1)
        self.clf = PairClassifier(self.dp, filename='data/randomforest.clf')
        self.al = AnnotationLoader()
        self.annotations, self.ann_x, self.ann_y = self.al.get_annotations(
            "data/sequences/simulated_alignment.js"
        )
        self.emission_table = None

    def emission(self, seq_x, x, dx, seq_y, y, dy):
        #if(dx!=1 && dy!=1) raise SomeException

        if x >= len(seq_x) or y >= len(seq_y):
            sys.stderr.write("WARNING: index out of bounds\n")
            return 0

        if self.emission_table is None:
            return self.clf.prepare_predict(
                seq_x, x, self.ann_x, seq_y, y, self.ann_y
            )
        else:
            return self.emission_table.get(x, y)

    def set_emission_table(self, emission_table):
        self.emission_table = emission_table


class SimpleState(GeneralizedPairState):
    def emission(self, *_, **__):
        return 1
