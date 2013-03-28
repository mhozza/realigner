'''
Created on Mar 22, 2013

@author: Michal Hozza
'''

import sys
from numpy import array, mean
from copy import deepcopy
from sklearn.ensemble import RandomForestClassifier

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

def printMulti(*i):    
    print(i)


X, y = prepare_data()

clf = RandomForestClassifier(n_estimators=1000, n_jobs=4)
clf.fit(X, y)

s,e = (45,95)
testSet = X[s:e]
hits = array([tree.predict(testSet) for tree in clf.estimators_])
means = [mean(hits[:,i]) for i in range(len(testSet))]
yy = clf.predict_proba(testSet)[:,1]

#print table
map(printMulti, y[s:e], means, yy)

# scores = cross_val_score(clf, X, y)
# print scores.mean()
