'''
Created on Mar 28, 2013

@author: Michal Hozza
'''
from alignment import Fasta
from alignment.Alignment import Alignment
from copy import deepcopy
from numpy import array
from os import path, listdir
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

    def toTrainData(self, last):
        m = {'A':0, 'C':1, 'G':2, 'T':3, '-':-1}

        if(self.base!='-'):
            last.copy(self)
        res = [m[last.base]]
        for i in self.annotations:
            res.append(self.annotations[i])
        return res


class AnnotatedBaseCouple:
    def __init__(self, annotations = []):
        self.annotations = annotations
        self.X = AnnotatedBase()
        self.Y = AnnotatedBase()

    def toTrainData(self, lastX, lastY):
        return array(list(itertools.chain(*zip(self.X.toTrainData(lastX), self.Y.toTrainData(lastY)))))

    def isAligned(self):
        return self.X.base != '-' != self.Y.base


class PairClassifier:
    def __init__(self, filename="data/random_forest.clf",
                 trainingDataDir="data/train_sequences",
                 params={"n_estimators":10, "n_jobs":4}):
        self.defaultFilename = filename
        self.trainingDataDir = trainingDataDir
        self.params = params
        self.mem = dict()

        if path.exists(self.defaultFilename):
            if path.isfile(self.defaultFilename):
                self.load(self.defaultFilename)
        else:
            self.classifier = RandomForestClassifier(**self.params)
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
        self.classifier = RandomForestClassifier(**self.params)

    def fit(self, data, target):
        self.classifier.fit(data, target)

    def predict(self, data):
        d = tuple(data)
        if d in self.mem:
            return self.mem[d]
                
#    	return self.classifier.predict(data)
#        hits = array([tree.predict(data) for tree in self.classifier.estimators_])
#        return [mean(hits[:,i]) for i in range(len(data))]
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

    def _SequenceToAnnotatedBaseCoupleList(self, annotations, seqX, annotationsX,
                                           seqY, annotationsY):
        if len(seqX) != len(seqY):
            print seqX
            print seqY
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
        #TODO - vyriesit pripad ked niektora sekvencia zacina -
        lastX, lastY = (AnnotatedBase(), AnnotatedBase())
        for i in abcList:
            train_data[0].append(i.toTrainData(lastX, lastY))
            train_data[1].append(i.isAligned())
        return train_data

    def loadDirectory(self, dirname):
        sequences = list()
        for fn in listdir(dirname):
            fname = path.join(dirname, fn)
            if path.isfile(fname):
                sequences.append(self.loadSequence(fname))
        return sequences


if __name__ == "__main__":
    dirname = "../data/train_sequences"
    if not path.isdir(dirname):
        sys.stderr.write("ERROR: invalid directory name\n")
        exit(1)

    c = PairClassifier()

    print c.predict([0, 0, 1, 1])
    print c.predict([0, 0, 1, 0])
    print c.predict([0, 0, 0, 1])
    print c.predict([0, 0, 0, 0])
    print c.predict([1, 0, 1, 1])
    print c.predict([1, 0, 1, 0])
    print c.predict([1, 0, 0, 1])
    print c.predict([1, 0, 0, 0])
    # print (d.getSequences(fname))
