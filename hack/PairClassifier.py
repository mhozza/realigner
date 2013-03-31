'''
Created on Mar 28, 2013

@author: Michal Hozza
'''
from alignment import Fasta
from alignment.Alignment import Alignment
from copy import deepcopy
from os import path, listdir
from sklearn.ensemble import RandomForestClassifier
import pickle
import sys


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
#    def __init__(self):


    def _SequencetoAnnotatedBaseCoupleList(self,seqX, annotationsX,
                                           seqY, annotationsY):
        pass

    def _getAnnotations(self, fname):
        return (None,None)

    def _getSequencesAlignment(self, fname):
        alignment_regexp = ""
        sequence_regexp = ["sequence1", "sequence2"]

        #pre zaciatok berieme len prve zarovnanie
        aln = Fasta.load(fname, alignment_regexp, Alignment, sequence_regexp ).next()
        if aln==None or len(aln.sequences) < 2:
            sys.stderr.write("ERROR: not enough sequences in file\n")
            exit(1)

        # Sequence 1
        seq1 = aln.sequences[0]

        # Sequence 2
        seq2 = aln.sequences[1]

        return (seq1, seq2)


    def loadSequence(self, fname):
        #constants
        annotationsSubdirName = "annotations"

        base = path.basename(fname)
        directory = path.dirname(fname)
        annotationsFname = path.join(directory,annotationsSubdirName,base)

        seqX, seqY = self._getSequencesAlignment(fname)
        annotationsX, annotationsY = self._getAnnotations(annotationsFname)

        return self._SequencetoAnnotatedBaseCoupleList(seqX, annotationsX, seqY,
                                                       annotationsY)


    def loadDirectory(self, dirname):
        sequences = []
        for fname in listdir(dirname):
            if path.isfile(fname):
                sequences.append(self.loadSequence(fname))
        return sequences


if __name__ == "__main__":
    fname = "../working_dir_tmp/sampled_alignments/0.fa"
    if not path.isfile(fname):
        sys.stderr.write("ERROR: invalid file name\n")
        exit(1)

    d = DataLoader()
    d.loadSequence(fname)
    print (d._getSequencesAlignment(fname))
