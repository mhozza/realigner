'''
Created on Mar 28, 2013

@author: Michal Hozza
'''
from alignment import Fasta
from alignment.Alignment import Alignment
from copy import deepcopy
from numpy import array
from numpy.ma.core import mean
from os import path, listdir
from random import randint
from sklearn.ensemble import RandomForestClassifier
import itertools
import os
import pickle
import sys

class AnnotatedBase:
    def __init__(self):
        self.base = '-'
        self.annotations = {}

    def copy(self, ab):
        self.base = ab.base
        self.annotations = deepcopy(ab.annotations)

    def toTrainData(self):
        gap_val = -1  # hodnota kotrou sa ma nahradit '-'
        m = {'A':0, 'C':1, 'G':2, 'T':3, '-':gap_val}
        res = [m[self.base]]
        for i in self.annotations.values():
            if i=='-':
                res.append(gap_val)
            else:
                res.append(float(i))
        return res


class AnnotatedBaseCouple:
    def __init__(self, annotations = []):
        self.annotations = annotations
        self.X = AnnotatedBase()
        self.Y = AnnotatedBase()

    def toTrainData(self):
        return array(list(itertools.chain(*zip(self.X.toTrainData(), self.Y.toTrainData()))))

    def isAligned(self):
        if(self.X.base != '-' != self.Y.base):
            return 1
        else:
            return 0


class PairClassifier:
    def _getClassifier(self):
        return RandomForestClassifier(**self.params)

    def __init__(self, filename="data/randomforest.clf",
                 trainingDataDir="data/train_sequences",
                 params={"n_estimators":1000, "n_jobs":4}, autotrain=True):
        self.defaultFilename = filename
        self.trainingDataDir = trainingDataDir
        self.params = params
        self.mem = dict()

        if autotrain and path.exists(self.defaultFilename):
            if path.isfile(self.defaultFilename):
                self.load(self.defaultFilename)
        else:
            self.classifier = self._getClassifier()
            if autotrain:
                dl = DataLoader()
                data, target = (list(), list())
                for seq in dl.loadDirectory(self.trainingDataDir):
                    d, t = dl.prepareTrainingData(seq)
                    data += d
                    target += t
                self.fit(data, target)
                self.save(self.defaultFilename)

    def load(self, fname):
        f = open(fname,'r')
        self.classifier = pickle.load(f)
        f.close()

    def save(self, fname):
        f = open(fname,'w')
        pickle.dump(self.classifier, f)
        f.close()

    def removeDefaultFile(self):
        os.remove(self.defaultFilename)

    def reset(self):
        if self.classifier:
            del self.classifier
        self.classifier = self._getClassifier()

    def fit(self, data, target):
        self.classifier.fit(data, target)

    def predict(self, data):
        d = tuple(data)
        if d in self.mem:
            return self.mem[d]

#    	return self.classifier.predict(data)
#        hits = array([tree.predict(data) for tree in self.classifier.estimators_])
#        res = [mean(hits[:,i]) for i in range(len(data))]
        res =  self.classifier.predict_proba(data)[:,1]
        self.mem[d] = res
        return res


class DataLoader:
    def getAnnotationsAt(self, annotations, i):
        baseAnnotation = dict()
        if annotations != None:
            for key in annotations:
                baseAnnotation[key] = annotations[key][i]
        return baseAnnotation

    def alnToAnnotation(self, annotations):
        newannotations = dict()
        for key in annotations:
            newannotations[key] =  annotations[key].replace("-","")
        return newannotations

    def _SequenceToAnnotatedBaseCoupleList(self, annotations, seqX, annotationsX,
                                           seqY, annotationsY):
        if len(seqX) != len(seqY):
            print(seqX)
            print(seqY)
            sys.stderr.write("ERROR: sequences does not have same length\n")
            exit(1)

        data = list()

        for i in range(len(seqX)):
            b = AnnotatedBaseCouple(annotations)
            b.X.base = seqX[i]
            b.X.annotations = self.getAnnotationsAt(annotationsX, i)
            b.Y.base = seqY[i]
            b.Y.annotations = self.getAnnotationsAt(annotationsY, i)
            data.append(b)
        return data


    def getAnnotations(self, fname):
        annotationsCount = 0
        annotationNames = list()
        annotationsX, annotationsY = dict(), dict()
        if path.isfile(fname):
            f = open(fname,'r')
            for i, line in enumerate(f):
                if i==0:
                    annotationsCount = int(line)
                elif i<=annotationsCount:
                    annotationNames.append(line.strip())
                elif i<=2*annotationsCount:
                    annotationsX[annotationNames[i-1-annotationsCount]] = line.strip()
                else:
                    annotationsY[annotationNames[i-1-2*annotationsCount]] = line.strip()
            f.close()
        return (annotationsX, annotationsY)

    def getSequences(self, fname):
        alignment_regexp = ""
        sequence_regexp = ["sequence1", "sequence2"]

        #pre zaciatok berieme len prve zarovnanie
        aln = Fasta.load(fname, alignment_regexp, Alignment, sequence_regexp ).next()
        if aln==None or len(aln.sequences) < 2:
            sys.stderr.write("ERROR: not enough sequences in file\n")
            exit(1)
        seq1 = aln.sequences[0]
        seq2 = aln.sequences[1]
        return (seq1, seq2)


    def loadSequence(self, fname):
        #constants
        annotationsSubdirName = "annotations"
        annotations = ["Gene"]

        base = path.basename(fname)
        directory = path.dirname(fname)
        annotationsFname = path.join(directory,annotationsSubdirName,base)

        seqX, seqY = self.getSequences(fname)
        annotationsX, annotationsY = self.getAnnotations(annotationsFname)
        return self._SequenceToAnnotatedBaseCoupleList(annotations,
                                                       seqX, annotationsX,
                                                       seqY, annotationsY)

    def prepareTrainingData(self, abcList):
        train_data = (list(), list())        
        for i in abcList:
            if i.isAligned():
                train_data[0].append(i.toTrainData())
                train_data[1].append(1)

        seq_size = len(train_data[0])
        for i in range(seq_size):
            x = (randint(0,seq_size-1))
            y = (randint(0,seq_size-1))
            if x!=y:
                b = AnnotatedBaseCouple(abcList[0].annotations)
                b.X = abcList[x].X
                b.Y = abcList[y].Y
                train_data[0].append(b.toTrainData())
                train_data[1].append(0)

        return train_data

    def loadDirectory(self, dirname):
        sequences = list()
        for fn in listdir(dirname):
            fname = path.join(dirname, fn)
            if path.isfile(fname):
                sequences.append(self.loadSequence(fname))
        return sequences


if __name__ == "__main__":
    c = PairClassifier(autotrain=False)    
    d = DataLoader()
#    x,y = d.prepareTrainingData(d.loadSequence("data/sequences/simulated_alignment.fa"))
    x,y = d.prepareTrainingData(d.loadSequence("data/sequences/short.fa"))
        
    c.fit(x,y)
    p = [array((i,j,k,l)) for i in range(4) for j in range(4) for k in range(2) for l in range(2)]
    yy = c.predict(p)
    for i in zip(p,yy):
        print(i)


