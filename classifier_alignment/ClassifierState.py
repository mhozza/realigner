from classifier_alignment.PairClassifier import PairClassifier
# from FakeClassifier import FakeMatchClassifier, FakeIndelClassifier
from hmm.PairHMM import GeneralizedPairState
from tools.Exceptions import ParseException
import constants
import config
from hmm.HMMLoader import getInitializerObject


class ClassifierState(GeneralizedPairState):
    def _get_classifier(self):
        return PairClassifier(
            self.dp,
            filename=self.clf_fname,
            use_global_classifier=config.same_classifier
        )
        # return FakeMatchClassifier(self.dp)

    def __init__(self, *args, **_):
        GeneralizedPairState.__init__(self, *args)
        self.dp = config.preparers[config.preparer_index][0](constants.window_size)
        self.clf_fname = 'data/clf/{}{}{}.clf'.format(
            PairClassifier.get_name(),
            config.preparers[config.preparer_index][2],
            constants.window_size,
        )
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

        return self.mathType(self._emission(c, seq_x, x, seq_y, y))

    def set_emission_table(self, emission_table):
        self.emission_table = emission_table


class ClassifierIndelState(ClassifierState):
    def _get_classifier(self):
        return PairClassifier(
            self.dp,
            filename=self.clf_fname,
            inverted=config.same_classifier,
            use_global_classifier=config.same_classifier
        )
        # return FakeIndelClassifier(self.dp)

    def _get_preparer(self, seq_num):
        if config.same_classifier:
            return config.preparers[config.preparer_index][0](constants.window_size)
        else:
            return config.preparers[config.preparer_index][1](seq_num, constants.window_size)

    def __init__(self, *args, **kwargs):
        ClassifierState.__init__(self, *args, **kwargs)
        self.dp = self._get_preparer(0)
        if config.same_classifier:
            suffix = ''
        else:
            suffix = '_indel'
        self.clf_fname = 'data/clf/{}{}{}{}.clf'.format(
            PairClassifier.get_name(),
            config.preparers[config.preparer_index][2],
            constants.window_size,
            suffix,
        )
        self.clf = self._get_classifier()

    def load(self, dictionary):
        res = ClassifierState.load(self, dictionary)
        if self.onechar == 'X':
            seq = 0
        elif self.onechar == 'Y':
            seq = 1
        else:
            raise ParseException('Invalid state onechar')
        self.dp = self.dp = self._get_preparer(seq)
        self.clf = self._get_classifier()
        return res


def register(loader):
    for obj in [ClassifierState, ClassifierIndelState]:
        loader.addFunction(obj.__name__, getInitializerObject(obj, loader.mathType))
