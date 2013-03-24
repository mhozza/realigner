'''
Created on Mar 22, 2013

@author: Michal Hozza
'''

import sys
from numpy import array
from collections import defaultdict
from copy import deepcopy
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_blobs
from sklearn.cross_validation import cross_val_score

SEQ_COUNT = 2
SEQ_DIMENSION = 2


class AnnotatedBase:
    def __init__(self):
        self.base = -1
        self.annotations = {}

    def copy(self, ab):
        self.base = ab.base
        self.annotations = deepcopy(ab.annotations)


class AnnotatedBaseCouple:
    def __init__(self, annotations = []):
        self.annotations = annotations
        self.X = AnnotatedBase()
        self.Y = AnnotatedBase()

    def toArray(self):
        a = [self.X.base, self.Y.base]

        for annotation in self.annotations:
            try:
                a.append(self.X.annotations[annotation])
            except KeyError, e:
                a.append(-1)

            try:
                a.append(self.Y.annotations[annotation])
            except KeyError, e:
                a.append(-1)
        return a


def fill_data(seq_data, last, i, seqnum):
    m = {'A':0, 'C':1, 'G':2, 'T':3, '-':-1}

    t = AnnotatedBase()

    csd = seq_data[seqnum]

    if csd[0][i]!='-':
        t.base = m[csd[0][i]]
        t.annotations["Gene"] = csd[1][i]
        last.copy(t)
    else:
        t = last
    return t

def prepare_data():
    seq_data = [[] for i in range(SEQ_COUNT)]
    for unused_var in range(SEQ_DIMENSION):
        for seqnum in range(SEQ_COUNT):
            seq_data[seqnum].append(sys.stdin.readline().strip())

    train_data = []
    target_data = []
    lastX, lastY = (AnnotatedBase(), AnnotatedBase())

    for i in range(len(seq_data[0][0])):
        target = 1.0
        if seq_data[0][0][i]=='-' or seq_data[1][0][i]=='-':
            target = 0.0

        train = AnnotatedBaseCouple(["Gene"])

        train.X = fill_data(seq_data, lastX, i, 0)
        train.Y = fill_data(seq_data, lastY, i, 1)

        train_data.append(train.toArray())
        target_data.append(target)

    return (array(train_data),array(target_data))


def printTwo(x,y):
    print(x,y, abs(x-y))



X, y = prepare_data()

# clf = RandomForestClassifier(n_estimators=10, max_depth=None, min_samples_split=1, random_state=0)
clf = RandomForestRegressor(n_estimators=111, min_samples_split=1, random_state=1)
clf.fit(X, y)

s,e = (45,95)
yy = clf.predict(X[s:e])


map(printTwo, y[s:e], yy)

# scores = cross_val_score(clf, X, y)
# print scores.mean()

