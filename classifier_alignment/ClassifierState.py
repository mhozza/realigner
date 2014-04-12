from classifier_alignment.PairClassifier import PairClassifier
from classifier_alignment.DataPreparer import DataPreparer, IndelDataPreparer
from hmm.PairHMM import GeneralizedPairState
from tools.Exceptions import ParseException
import constants
from FakeClassifier import FakeMatchClassifier, FakeIndelClassifier
from hmm.HMMLoader import getInitializerObject


class ClassifierState(GeneralizedPairState):
    def _get_classifier(self):
        return PairClassifier(self.dp, filename=self.clf_fname)
        # return FakeMatchClassifier(self.dp)

    def __init__(self, *args, **_):
        GeneralizedPairState.__init__(self, *args)
        self.dp = DataPreparer(constants.window_size)
        self.clf_fname = 'data/clf/randomforest{}.clf'.format(constants.window_size)
        self.clf = self._get_classifier()
        self.annotations, self.ann_x, self.ann_y = None, None, None
        self.emission_table = None

    def set_annotations(self, annotations):
        self.annotations, self.ann_x, self.ann_y = annotations

    def _emission(self, c, _, __, ___, ____):
        return c

    def emission(self, seq_x, x, dx, seq_y, y, dy):
        if self.emission_table is None:
            c = self.clf.prepare_predict(
                seq_x, x, self.ann_x, seq_y, y, self.ann_y
            )[0]
        else:
            c = self.emission_table.get(x, y)

        return self._emission(c, seq_x, x, seq_y, y)

    def set_emission_table(self, emission_table):
        self.emission_table = emission_table


class ClassifierIndelState(ClassifierState):
    # def _get_classifier(self):
    #     return FakeIndelClassifier(self.dp)

    def __init__(self, *args, **kwargs):
        ClassifierState.__init__(self, *args, **kwargs)
        self.dp = IndelDataPreparer(0, constants.window_size)
        self.clf_fname = 'data/clf/randomforest_indel{}.clf'.format(constants.window_size)
        self.clf = self._get_classifier()

    def load(self, dictionary):
        res = ClassifierState.load(self, dictionary)
        if self.onechar == 'X':
            seq = 0
        elif self.onechar == 'Y':
            seq = 1
        else:
            raise ParseException('Invalid state onechar')
        self.dp = IndelDataPreparer(seq, constants.window_size)
        self.clf = self._get_classifier()
        return res


def register(loader):
    for obj in [ClassifierState, ClassifierIndelState]:
        loader.addFunction(obj.__name__, getInitializerObject(obj, loader.mathType))
