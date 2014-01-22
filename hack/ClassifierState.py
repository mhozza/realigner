from hack.PairClassifier import PairClassifier
from hack.AnnotationLoader import AnnotationLoader
from hmm.PairHMM import GeneralizedPairState
import sys
from hack.DataPreparer import DataPreparer

window_size = 5


class ClassifierState(GeneralizedPairState):
    def __init__(self, *args, **_):
        GeneralizedPairState.__init__(self, *args)
        self.dp = DataPreparer(window_size)
        self.clf = PairClassifier(self.dp, filename='data/randomforest5.clf')
        self.al = AnnotationLoader()
        self.annotations, self.ann_x, self.ann_y = self.al.get_annotations(
            "data/sequences/simulated_alignment.js"
        )
        self.emission_table = None

    def _emission(self, _, __, c):
        return c

    def emission(self, seq_x, x, dx, seq_y, y, dy):
        #if(dx!=1 && dy!=1) raise SomeException
        if x >= len(seq_x) or y >= len(seq_y):
            sys.stderr.write("WARNING: index out of bounds\n")
            raise RuntimeError()

        if self.emission_table is None:
            c = self.clf.prepare_predict(
                seq_x, x, self.ann_x, seq_y, y, self.ann_y
            )
        else:
            c = self.emission_table.get(x, y)

        return self._emission(seq_x[x], seq_y[y], c)

    def set_emission_table(self, emission_table):
        self.emission_table = emission_table


class SimpleState(GeneralizedPairState):
    def emission(self, *_, **__):
        # 1/4 - base * 1/2 - gene
        # return (1/8.0)**window_size
        return 0.25
