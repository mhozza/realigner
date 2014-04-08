"""
@author: Michal Hozza
"""
from sklearn.utils import array2d
from sklearn.tree._tree import DTYPE
from classifier_alignment.DataPreparer import DataPreparer, IndelDataPreparer
from classifier_alignment.SimpleStates import SimpleMatchState, SimpleIndelState
import constants
from hmm.PairHMM import GeneralizedPairHMM
from tools.ConfigFactory import ConfigFactory
from tools.Exceptions import InvalidValueException


class JSLoader(ConfigFactory):
    def __init__(self, mathType=float):
        def getInitializerObject(tp, mathType):
            def __getInitializer(dictionary):
                t = tp(mathType)
                t.load(dictionary)
                return t
            return __getInitializer

        ConfigFactory.__init__(self)
        self.mathType = mathType
        for obj in [
            GeneralizedPairHMM,
            SimpleMatchState,
            SimpleIndelState,
        ]:

            self.addFunction(obj.__name__, getInitializerObject(obj, mathType))

        for (name, constant) in [
            # STUB
        ]:
            self.addConstant(name, constant)


class FakeMatchClassifier:
    def __init__(
        self,
        preparer,
        state_class=SimpleMatchState,
        model='data/models/SimpleHMM2.js',
    ):
        self._preparer = None
        self.preparer = preparer
        for state in JSLoader().load(model)['model'].states:
            if isinstance(state, state_class):
                self.emissions = state.emissions
                break

    def load(self, fname):
        pass

    def save(self, fname):
        pass

    def remove_default_file(self):
        pass

    @property
    def preparer(self):
        return self._preparer

    @preparer.setter
    def preparer(self, value):
        if value is None:
            self._preparer = DataPreparer(window=1)
        elif value is DataPreparer:
            self._preparer = value
        else:
            raise InvalidValueException('Value is not DataPreparer')

    @preparer.deleter
    def preparer(self):
        assert isinstance(self._preparer, DataPreparer)
        del self._preparer

    def reset(self):
        pass

    def fit(self, data, target):
        pass

    def prepare_predict(self, *args):
        return self.predict(self.preparer.prepare_data(*args))

    def multi_prepare_predict(self, data):
        prepared_data = [
            self.preparer.prepare_data(*args)
            for args in data
        ]

        return self.predict(prepared_data)

    def predict(self, X):
        if getattr(X, "dtype", None) != DTYPE or X.ndim != 2:
            X = array2d(X, dtype=DTYPE)
        # print [self.preparer.get_base(x) for x in X]
        return [self.emissions[self.preparer.get_base(x)] for x in X]


class FakeIndelClassifier(FakeMatchClassifier):
    def __init__(
            self,
            preparer,
            state_class=SimpleIndelState,
            model='data/models/SimpleHMM2.js',
    ):
        FakeMatchClassifier.__init__(self, preparer, state_class, model)


