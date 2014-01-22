import sys
from hack.PairClassifier import PairClassifier
from hack.AnnotationLoader import AnnotationLoader
from hack.DataPreparer import DataPreparer, IndelDataPreparer
from hmm.PairHMM import GeneralizedPairState
from tools.Exceptions import ParseException

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

    def _emission(self, _, __, ___, ____, c):
        return c

    def emission(self, seq_x, x, dx, seq_y, y, dy):
        if self.emission_table is None:
            c = self.clf.prepare_predict(
                seq_x, x, self.ann_x, seq_y, y, self.ann_y
            )
        else:
            c = self.emission_table.get(x, y)

        return self._emission(seq_x, x, seq_y, y, c)

    def set_emission_table(self, emission_table):
        self.emission_table = emission_table


class ClassifierIndelState(ClassifierState):
    def __init__(self, *args, **kwargs):
        ClassifierState.__init__(self, *args, **kwargs)
        self.dp = None
        self.clf = None

    def load(self, dictionary):
        res = ClassifierState.load(self, dictionary)
        if dictionary['name'] == 'InsertX':
            seq = 0
        elif dictionary['name'] == 'InsertY':
            seq = 1
        else:
            raise ParseException('Invalid state name')

        self.dp = IndelDataPreparer(seq, window_size)
        self.clf = PairClassifier(
            self.dp, filename='data/randomforest_indel5.clf'
        )

        return res


class SimpleState(GeneralizedPairState):
    def emission(self, *_, **__):
        # 1/4 - base * 1/2 - gene
        # return (1/8.0)**window_size
        return 0.25
