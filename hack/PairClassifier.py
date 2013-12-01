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


class PairClassifier:
    def _get_classifier(self):
        return RandomForestClassifier(**self.params)

    def __init__(
        self, filename="data/randomforest.clf",
        training_data_dir="data/train_sequences",
        params={"n_estimators": 100, "n_jobs": 4, "max_depth": 50}, autotrain=True,
        memoization=True,
    ):
        """

        @rtype : PairClassifier
        """
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
                for seq in dl.loadDirectory(self.training_data_dir):
                    d, t = dl.prepareTrainingData(seq)
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

    def reset(self):
        if self.classifier:
            del self.classifier
        self.classifier = self._get_classifier()

    def fit(self, data, target):
        self.classifier.fit(data, target)

    def predict(self, data):
        d = None
        if self.memoization:
            d = tuple(data)
            if d in self.mem:
                return self.mem[d]

            #    	return self.classifier.predict(data)
            #        hits = array([tree.predict(data) for tree in self.classifier.estimators_])
            #        res = [mean(hits[:,i]) for i in range(len(data))]
        res = self.classifier.predict_proba(data)[:, 1]
        if self.memoization:
            self.mem[d] = res
        return res



if __name__ == "__main__":
    pathToData = "../data/"
    c = PairClassifier(
        filename=pathToData + "randomforest.dat",
        training_data_dir=pathToData + "train_sequences",
        autotrain=False,
        memoization=False,
    )
    c2 = PairClassifier(
        filename=pathToData + "randomforest.dat",
        training_data_dir=pathToData + "train_sequences",
        autotrain=False,
        memoization=False,
    )

    dl = DataLoader()
    _, s_x, a_x, s_y, a_y = dl.loadSequence(pathToData + 'train_sequences/s1.fa')
    x, y = dl.prepareTrainingData(s_x, a_x, s_y, a_y, 1)
    _, s_x, a_x, s_y, a_y = dl.loadSequence(pathToData + "train_sequences/s1.fa", pathToData + "train_sequences/s1_na.js")
    x2, y2 = dl.prepareTrainingData(s_x, a_x, s_y, a_y, 1)

    #    x,y = d.prepareTrainingData(d.loadSequence(pathToData+"sequences/simulated_alignment.fa"),5)
    #    x2,y2 = d.prepareTrainingData(d.loadSequence(pathToData+"sequences/simulated_alignment.fa", pathToData+"sequences/simulated_alignment_na.js"),1)
    #    x,y = d.prepareTrainingData(d.loadSequence(pathToData+"sequences/short.fa"),5)
    #    x2,y2 = d.prepareTrainingData(d.loadSequence(pathToData+"sequences/short.fa", pathToData+"sequences/short_na.js"),5)
    px, py = dl.prepareTrainingData(dl.loadSequence(pathToData + "train_sequences/s2.fa"), 1)
    px2, py2 = dl.prepareTrainingData(
        dl.loadSequence(pathToData + "train_sequences/s2.fa", pathToData + "train_sequences/s2_na.js"), 1)

    #    print zip(x,y)
    #    px,py = x,y
    #    px2,py2 = x2,y2

    c.fit(x, y)
    c2.fit(x2, y2)
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
    dd21 = c2.predict([px2[i] for i in range(len(px2)) if py2[i]])
    dd20 = c2.predict([px2[i] for i in range(len(px2)) if not py2[i]])
    k1 = gaussian_kde(dd1)
    k0 = gaussian_kde(dd0)
    k21 = gaussian_kde(dd21)
    k20 = gaussian_kde(dd20)
    xvals = linspace(0.0, 1.0, 500)

    plt.subplot(1, 2, 1)
    plt.hist([dd1, dd0, dd21, dd20],
             10, normed=False, histtype='bar',
             stacked=False,
             label=["anotated 1", "anotated 0", "not anotated 1", "not anotated 0"])
    plt.legend(loc=0)
    plt.subplot(1, 2, 2)
    plt.hold(True)
    plt.plot(xvals, k1(xvals), label="anotated 1")
    plt.plot(xvals, k0(xvals), label="anotated 0")
    plt.plot(xvals, k21(xvals), label="not anotated 1")
    plt.plot(xvals, k20(xvals), label="not anotated 0")
    plt.legend(loc=0)
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


