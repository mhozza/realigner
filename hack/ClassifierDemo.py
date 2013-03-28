'''
Created on Mar 22, 2013

@author: Michal Hozza
'''

import sys
from numpy import array

from PairClassifier import AnnotatedBase, AnnotatedBaseCouple, PairClassifier

SEQ_COUNT = 2
SEQ_DIMENSION = 2


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

clf = PairClassifier()
X, y = prepare_data()
clf.fit(X,y)
s,e = (45,95)
testSet = X[s:e]
yy = clf.predict(testSet)
map(printMulti, y[s:e], yy)

