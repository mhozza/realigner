#/usr/bin/python
# coding=utf-8
"""
Created on Mar 28, 2013

@author: Michal Hozza
"""
import os
import sys
import pickle
from os import path
from numpy import array
from scipy.stats.kde import gaussian_kde
import matplotlib.pyplot as plt
from classifier_alignment.DataLoader import DataLoader
from classifier_alignment.DataPreparer import DataPreparer
from classifier_alignment import plot_utils
from tools.Exceptions import InvalidValueException
import config
import constants

_global_classifier = None


class PairClassifier:
    def _get_classifier(self):
        return config.classifiers[config.classifier_index][0](**self.params)

    def __init__(
        self,
        preparer,
        filename="data/clf/randomforest.clf",
        training_data_dir="data/sequences/train_sequences",
        params=None,
        autotrain=True,
        memoization=False,
        inverted=False,
        use_global_classifier=False,
    ):
        global _global_classifier
        """
        @rtype : PairClassifier
        """
        self._preparer = None
        self.preparer = preparer
        self.default_filename = filename
        self.training_data_dir = training_data_dir
        if params is None:
            self.params = config.classifiers[config.classifier_index][2]
        else:
            self.params = params
        self.mem = dict()
        self.memoization = memoization
        self.inverted = inverted

        if _global_classifier is None or not use_global_classifier:
            if autotrain and path.exists(self.default_filename):
                if path.isfile(self.default_filename):
                    self.load(self.default_filename)
            else:
                self.classifier = self._get_classifier()
                if autotrain:
                    sys.stderr.write('Training clasifier\n')
                    dl = DataLoader()
                    data, target, weights = list(), list(), list()
                    sequences = dl.loadDirectory(self.training_data_dir)
                    for _, s_x, a_x, s_y, a_y in sequences:
                        d, t, w = self.preparer.prepare_training_data(
                            s_x, a_x, s_y, a_y
                        )
                        data += d
                        target += t
                        weights += w
                    self.fit(data, target, array(weights))
                    self.save(self.default_filename)
            if use_global_classifier:
                _global_classifier = self.classifier
        else:
            self.classifier = _global_classifier

    @staticmethod
    def get_name():
        return config.classifiers[config.classifier_index][1]

    def load(self, fname):
        with open(fname, 'r') as f:
            self.classifier = pickle.load(f)
            # print 'Clf loaded form file.'

    def save(self, fname):
        with open(fname, 'w') as f:
            pickle.dump(self.classifier, f)

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

    def fit(self, data, target, sample_weight=None):
        self.classifier.fit(data, target, sample_weight)
        print (self.classifier.score(data, target))

    def score(self, data, target):
        return self.classifier.score(data, target)

    def prepare_predict(self, *args):
        return self.predict(self.preparer.prepare_data(*args))

    def multi_prepare_predict(self, data):
        prepared_data = [
            self.preparer.prepare_data(*args)
            for args in data
        ]

        return self.predict(prepared_data, False)

    def predict(self, data, memoization=None):
        if len(data) == 0:
            return []
        d = None
        if memoization is None:
            memoization = self.memoization
        if memoization:
            d = tuple(data)
            if d in self.mem:
                return self.mem[d]

        # res = self.classifier.predict(data)
        res = self.classifier.predict_proba(data)[:, 1]
        if self.inverted:
            res = [1 - i for i in res]

        if memoization:
            self.mem[d] = res
        return res

pic_suffix = '.eps'


def compute_graph_data(clf, data):
    hist = clf.predict([data[i] for i in range(len(data))])
    gaus = gaussian_kde(hist)
    return hist, gaus


def compute_01graph_data(clf, data, target):
    hist0 = clf.predict([data[i] for i in range(len(data)) if not target[i]])
    hist1 = clf.predict([data[i] for i in range(len(data)) if target[i]])
    # gaus0 = gaussian_kde(hist0)
    # gaus1 = gaussian_kde(hist1)
    gaus0, gaus1 = None, None
    return hist0, hist1, gaus0, gaus1


def plot_clf(dp, x, y, fname=None):
    if fname is None:
        autotrain = False
    else:
        autotrain = True

    c = PairClassifier(
        preparer=dp,
        filename=fname,
        autotrain=autotrain,
    )
    if fname is None:
        c.fit(x, y)
    plot_utils.plot(*compute_01graph_data(c, x, y))
    print c.score(x, y)
    return c


def main(preparer_index):
    path_to_data = "data/"
    dp = config.preparers[preparer_index][0](constants.window_size)
    clf_fname = 'data/clf/{}{}{}.clf'.format(
        PairClassifier.get_name(),
        config.preparers[preparer_index][2],
        constants.window_size,
    )
    idp = config.preparers[preparer_index][1](0, constants.window_size)
    iclf_fname = 'data/clf/{}{}{}{}.clf'.format(
        PairClassifier.get_name(),
        config.preparers[preparer_index][2],
        constants.window_size,
        '_indel',
    )
    dl = DataLoader()
    # _, s_x, a_x, s_y, a_y = dl.loadSequence(
    #     path.join(path_to_data, 'sequences/train_sequences/simulated_alignment0.fa'),
    # )

    # x, y, _ = dp.prepare_training_data(s_x, a_x, s_y, a_y)
    # ix, iy, _ = idp.prepare_training_data(s_x, a_x, s_y, a_y)

    # c.fit(x, y)
    # ic.fit(ix, iy)

    _, s_x, a_x, s_y, a_y = dl.loadSequence(
        path.join(path_to_data, 'sequences/model_train_seq/simulated/simulated_alignment.fa')
    )
    px, py, _ = dp.prepare_training_data(s_x, a_x, s_y, a_y)
    ipx, ipy, _ = idp.prepare_training_data(s_x, a_x, s_y, a_y)

    # plot(*compute_01graph_data(c, x, y))
    # plot(*compute_01graph_data(ic, ix, iy))

    # plot(*compute_01graph_data(c, px, py))
    # plot(*compute_01graph_data(ic, ipx, ipy))
    plot_clf(dp, px, py, clf_fname)
    plt.savefig(
        path.splitext(clf_fname)[0] + "_test" + pic_suffix, transparent=True, bbox_inches='tight'
    )
    plot_clf(idp, ipx, ipy, iclf_fname)
    plt.savefig(
        path.splitext(iclf_fname)[0] + "_test" + pic_suffix, transparent=True, bbox_inches='tight'
    )
    plt.show()

if __name__ == "__main__":
    main(config.preparer_index)
