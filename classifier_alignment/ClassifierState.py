from classifier_alignment.PairClassifier import PairClassifier
from classifier_alignment.AnnotationLoader import AnnotationLoader
from classifier_alignment.DataPreparer import DataPreparer, IndelDataPreparer
from hmm.PairHMM import GeneralizedPairState
from tools.Exceptions import ParseException

window_size = 5


class ClassifierState(GeneralizedPairState):
    def __init__(self, *args, **_):
        GeneralizedPairState.__init__(self, *args)
        self.dp = DataPreparer(window_size)
        self.clf_fname = 'data/clf/randomforest{}.clf'.format(window_size)
        self.clf = PairClassifier(self.dp, filename=self.clf_fname)
        self.al = AnnotationLoader()
        # Fixme
        self.annotations, self.ann_x, self.ann_y = self.al.get_annotations(
            "data/sequences/simulated/simulated_alignment.js"
        )
        self.emission_table = None

    def _emission(self, c, _, __, ___, ____):
        return c

    def emission(self, seq_x, x, dx, seq_y, y, dy):
        if self.emission_table is None:
            c = self.clf.prepare_predict(
                seq_x, x, self.ann_x, seq_y, y, self.ann_y
            )
        else:
            c = self.emission_table.get(x, y)

        return self._emission(c, seq_x, x, seq_y, y)

    def set_emission_table(self, emission_table):
        self.emission_table = emission_table


class ClassifierIndelState(ClassifierState):
    def __init__(self, *args, **kwargs):
        ClassifierState.__init__(self, *args, **kwargs)
        self.dp = IndelDataPreparer(0, window_size)
        self.clf_fname = 'data/clf/randomforest_indel{}.clf'.format(window_size)
        self.clf = PairClassifier(
            self.dp, filename=self.clf_fname
        )

    def load(self, dictionary):
        res = ClassifierState.load(self, dictionary)
        if self.onechar == 'X':
            seq = 0
        elif self.onechar == 'Y':
            seq = 1
        else:
            raise ParseException('Invalid state onechar')
        self.dp = IndelDataPreparer(seq, window_size)
        self.clf = PairClassifier(
            self.dp, self.clf_fname
        )

        return res
