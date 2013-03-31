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
        for i in self.annotations.keys():
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
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=10, n_jobs=4)

    def load(self, f):
        self.classifier = pickle.load(f)

    def save(self, f):
        pickle.dump(self.classifier, f)

    def fit(self, data, target):
        self.classifier.fit(data, target)

    def predict(self, data):
#    	return self.classifier.predict(data)
#        hits = array([tree.predict(data) for tree in self.classifier.estimators_])
#        return [mean(hits[:,i]) for i in range(len(data))]
        return self.classifier.predict_proba(data)


class DataLoader:
    def _getAnotationsAt(self, annotations, i):
        baseAnnotation = dict()
        if annotations != None:            
            for key in annotations.keys():
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
            b.X.annotations = self._getAnotationsAt(annotationsX, i)
            b.Y.base = seqY[i]
            b.Y.annotations = self._getAnotationsAt(annotationsY, i)
            data.append(b)

        return data


    def _getAnnotations(self, fname):
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

    def _getSequencesAlignment(self, fname):
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

        seqX, seqY = self._getSequencesAlignment(fname)
        annotationsX, annotationsY = self._getAnnotations(annotationsFname)
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
    dirname = name = "../data/train_sequences"
    if not path.isdir(dirname):
        sys.stderr.write("ERROR: invalid directory name\n")
        exit(1)

    d = DataLoader()
    seqs = d.loadDirectory(dirname)
    seq = seqs[0]
    data, target = d.prepareTrainingData(seq)
    for i,j,s in zip(data, target, seq):
        print i, s.X.base, s.X.annotations, s.Y.base, s.Y.annotations, j
    # print (d._getSequencesAlignment(fname))
