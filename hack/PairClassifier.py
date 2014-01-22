#/usr/bin/python
"""
Created on Mar 28, 2013

@author: Michal Hozza
"""
from numpy.core.function_base import linspace
from os import path
from scipy.stats.kde import gaussian_kde
import os
import pickle

from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from hack.DataLoader import DataLoader
from hack.DataPreparer import DataPreparer
from tools.Exceptions import InvalidValueException


class PairClassifier:
    def _get_classifier(self):
        return RandomForestClassifier(**self.params)

    def __init__(
        self,
        preparer=None,
        filename="data/randomforest.clf",
        training_data_dir="data/train_sequences",
        params={"n_estimators": 10, "n_jobs": 10, "max_depth": 20},
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
                dl = DataLoader()
                data, target = (list(), list())
                sequences = dl.loadDirectory(self.training_data_dir)
                for _, s_x, a_x, s_y, a_y in sequences:
                    d, t = dl.prepareTrainingData(
                        s_x, a_x, s_y, a_y, self.preparer
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

        res = self.classifier.predict_proba(data)[:, 1]

        if memoization:
            self.mem[d] = res
        return res


def main():
    path_to_data = "data/"
    c = PairClassifier(
        filename=path_to_data + "randomforest.dat",
        training_data_dir=path_to_data + "train_sequences",
        autotrain=False,
        memoization=False,
    )
    #c2 = PairClassifier(
    #    filename=path_to_data + "randomforest.dat",
    #    training_data_dir=path_to_data + "train_sequences",
    #    autotrain=False,
    #    memoization=False,
    #)

    dl = DataLoader()
    dp = DataPreparer(5)
    _, s_x, a_x, s_y, a_y = dl.loadSequence(
        path_to_data + 'train_sequences/simulated_alignment.fa'
    )
    x, y = dl.prepareTrainingData(s_x, a_x, s_y, a_y, dp)
    print x, y
    #_, s_x, a_x, s_y, a_y = dl.loadSequence(path_to_data + "train_sequences/s1.fa", path_to_data + "train_sequences/s1_na.js")
    #x2, y2 = dl.prepareTrainingData(s_x, a_x, s_y, a_y, dp)

    #    x,y = d.prepareTrainingData(d.loadSequence(path_to_data+"sequences/simulated_alignment.fa"),5)
    #    x2,y2 = d.prepareTrainingData(d.loadSequence(path_to_data+"sequences/simulated_alignment.fa", path_to_data+"sequences/simulated_alignment_na.js"),1)
    #    x,y = d.prepareTrainingData(d.loadSequence(path_to_data+"sequences/short.fa"),5)
    #    x2,y2 = d.prepareTrainingData(d.loadSequence(path_to_data+"sequences/short.fa", path_to_data+"sequences/short_na.js"),5)
    _, s_x, a_x, s_y, a_y = dl.loadSequence(
        path_to_data + 'sequences/simulated_alignment.fa'
    )
    print _, s_x, a_x, s_y, a_y
    px, py = dl.prepareTrainingData(s_x, a_x, s_y, a_y, dp)
    print px, py
    #px2, py2 = dl.prepareTrainingData(
    #    dl.loadSequence(path_to_data + "train_sequences/s2.fa", path_to_data + "train_sequences/s2_na.js"), dp)

    #    print zip(x,y)
    #    px,py = x,y
    #    px2,py2 = x2,y2

    c.fit(x, y)

    #c2.fit(x2, y2)
    # p = [array((i,j,k,l)) for k in range(2) for l in range(2) for i in range(4) for j in range(4) ]
    # yy = c.predict(p)

    # for i,j in enumerate(yy):
    #     if i % 16 ==0:
    #         s = 0
    #     s+=j
    #     if i % 16 ==15:
    #         for k in range(i-15, i+1):
    #             yy[k]*=4
    #             yy[k]/=s

    # for i in zip(p,yy):
    #     print(i)
    dd1 = c.predict([px[i] for i in range(len(px)) if py[i]])
    dd0 = c.predict([px[i] for i in range(len(px)) if not py[i]])
    #dd21 = c2.predict([px2[i] for i in range(len(px2)) if py2[i]])
    #dd20 = c2.predict([px2[i] for i in range(len(px2)) if not py2[i]])
    k1 = gaussian_kde(dd1)
    k0 = gaussian_kde(dd0)
    #k21 = gaussian_kde(dd21)
    #k20 = gaussian_kde(dd20)
    xvals = linspace(0.0, 1.0, 500)

    plt.subplot(1, 2, 1)
    plt.hist(
        [
            dd1,
            dd0,
            # dd21,
            # dd20
        ],
        10,
        normed=False,
        histtype='bar',
        stacked=False,
        label=["anotated 1", "anotated 0", "not anotated 1", "not anotated 0"])
    plt.legend(loc=0)
    plt.subplot(1, 2, 2)
    plt.hold(True)
    plt.plot(xvals, k1(xvals), label="anotated 1")
    plt.plot(xvals, k0(xvals), label="anotated 0")
    #plt.plot(xvals, k21(xvals), label="not anotated 1")
    #plt.plot(xvals, k20(xvals), label="not anotated 0")
    #plt.legend(loc=0)
    plt.show()


    # plt.plot(histogram(yy, 100, density=False)[0])
    # k = gaussian_kde(yy)
    # xvals = linspace(0, 1, 100)
    # plt.hold(True)
    # plt.plot(k(xvals))

#    plt.show()


#     zt = [0.65, 0.7, 0.8]

#     b = list()

#     for g1 in [0,1]:
#         for g2 in [0,1]:
#             z = zt[g1+g2]
#             a = [[0.0 for i in range(4)] for j in range(4)]
#             for i in range(4):
#                 a[i][i] +=z**2
#                 for j in range(4):
#                     if i!=j:
#                         a[i][j] += 2*z*(1-z)/3
#                         for k in range(4):
#                             if k!=i:
#                                 a[j][k] += ((1-z)**2)/9

#             for r in enumerate(a):
#                 for c in enumerate(r[1]):
#                     print(r[0],c[0],g1,g2,c[1])
#                     b.append(c[1])
#                     # print(r[0],c[0],g1,g2,c[1]*pt[g1+g2]*.25)


#     # plt.plot(histogram(b, 100, density=True)[0])
#     # plt.hold(True)
#     plt.plot(histogram(b, 100, density=False)[0])
#     k = gaussian_kde(b)
#     xvals = linspace(0, 1, 100)
#     plt.plot(k(xvals))
#     plt.show()


if __name__ == "__main__":
    main()
