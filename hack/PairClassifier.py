#/usr/bin/python
"""
Created on Mar 28, 2013

@author: Michal Hozza
"""
import os
import sys
import pickle
from os import path
from numpy.core.function_base import linspace
from scipy.stats.kde import gaussian_kde

from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from hack.DataLoader import DataLoader
from hack.DataPreparer import DataPreparer, IndelDataPreparer
from tools.Exceptions import InvalidValueException


class PairClassifier:
    def _get_classifier(self):
        return RandomForestRegressor(**self.params)

    def __init__(
        self,
        preparer,
        filename="data/randomforest.clf",
        training_data_dir="data/train_sequences",
        params={"n_estimators": 50, "n_jobs": 10, "max_depth": 20},
        autotrain=True,
        memoization=True,
    ):
        """

        @rtype : PairClassifier
        """
        self._preparer = None
        self.preparer = preparer
        self.default_filename = filename
        self.training_data_dir = training_data_dir
        self.params = params
        self.mem = dict()
        self.memoization = memoization

        if autotrain and path.exists(self.default_filename):
            if path.isfile(self.default_filename):
                self.load(self.default_filename)
        else:
            self.classifier = self._get_classifier()
            if autotrain:
                sys.stderr.write('Training clasifier\n')
                dl = DataLoader()
                data, target = (list(), list())
                sequences = dl.loadDirectory(self.training_data_dir)
                for _, s_x, a_x, s_y, a_y in sequences:
                    d, t = self.preparer.prepare_training_data(
                        s_x, a_x, s_y, a_y
                    )
                    data += d
                    target += t
                self.fit(data, target)
                self.save(self.default_filename)

    def load(self, fname):
        f = open(fname, 'r')
        self.classifier = pickle.load(f)
        f.close()

    def save(self, fname):
        f = open(fname, 'w')
        pickle.dump(self.classifier, f)
        f.close()

    def remove_default_file(self):
        os.remove(self.default_filename)

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
        if self.classifier:
            del self.classifier
        self.classifier = self._get_classifier()

    def fit(self, data, target):
        self.classifier.fit(data, target)

    def prepare_predict(self, *args):
        return self.predict(self.preparer.prepare_data(*args))

    def multi_prepare_predict(self, data):
        prepared_data = [
            self.preparer.prepare_data(*args)
            for args in data
        ]

        return self.predict(prepared_data, False)

    def predict(self, data, memoization=None):
        d = None
        if memoization is None:
            memoization = self.memoization
        if memoization:
            d = tuple(data)
            if d in self.mem:
                return self.mem[d]

        res = self.classifier.predict(data)

        if memoization:
            self.mem[d] = res
        return res


def plot(hist0, hist1, gaus0, gaus1):
    xvals = linspace(0.0, 1.0, 500)

    plt.figure()
    plt.subplot(1, 2, 1)
    plt.hist(
        [
            hist1,
            hist0,
        ],
        10,
        normed=False,
        histtype='bar',
        stacked=False,
        label=["anotated 1", "anotated 0", "not anotated 1", "not anotated 0"])
    plt.legend(loc=0)
    plt.subplot(1, 2, 2)
    plt.hold(True)
    plt.plot(xvals, gaus1(xvals), label="anotated 1")
    plt.plot(xvals, gaus0(xvals), label="anotated 0")


def compute_graph_data(clf, data, target):
    hist0 = clf.predict([data[i] for i in range(len(data)) if not target[i]])
    hist1 = clf.predict([data[i] for i in range(len(data)) if target[i]])
    gaus0 = gaussian_kde(hist0)
    gaus1 = gaussian_kde(hist1)
    return hist0, hist1, gaus0, gaus1


def main():
    path_to_data = "data/"
    c = PairClassifier(
        preparer=None,
        filename=path.join(path_to_data, "randomforest.dat"),
        training_data_dir=path.join(path_to_data, "train_sequences"),
        autotrain=False,
        memoization=False,
    )

    ic = PairClassifier(
        preparer=None,
        filename=path.join(path_to_data, "randomforest.dat"),
        training_data_dir=path.join(path_to_data, "train_sequences"),
        autotrain=False,
        memoization=False,
    )

    window_size = 5
    dl = DataLoader()
    dp = DataPreparer(window_size)
    idp = IndelDataPreparer(0, window_size)

    _, s_x, a_x, s_y, a_y = dl.loadSequence(
        path.join(path_to_data, 'train_sequences/simulated_alignment.fa'),
    )
    x, y = dp.prepare_training_data(s_x, a_x, s_y, a_y)
    ix, iy = idp.prepare_training_data(s_x, a_x, s_y, a_y)

    for i in zip(x, y):
        print(i)

    c.fit(x, y)
    ic.fit(ix, iy)

    plot(*compute_graph_data(c, x, y))
    plot(*compute_graph_data(ic, ix, iy))

    _, s_x, a_x, s_y, a_y = dl.loadSequence(
        path.join(path_to_data, 'sequences/simulated_alignment.fa')
    )

    px, py = dp.prepare_training_data(s_x, a_x, s_y, a_y)
    ipx, ipy = idp.prepare_training_data(s_x, a_x, s_y, a_y)

    plot(*compute_graph_data(c, px, py))
    plot(*compute_graph_data(ic, ipx, ipy))
    plt.show()

if __name__ == "__main__":
    main()
