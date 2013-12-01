"""
Created on May 10, 2013

@author: Michal Hozza
"""
from alignment import Fasta
from alignment.Alignment import Alignment
from copy import deepcopy
from numpy import array
from os import path, listdir
from random import randint

import itertools
import sys
from hack.AnnotationLoader import AnnotationLoader
from hack.DataPreparer import DataPreparer


class AnnotatedBase:
    def __init__(self):
        self.base = '-'
        self.annotations = {}
        self.position = 0

    def copy(self, ab):
        self.base = ab.base
        self.annotations = deepcopy(ab.annotations)
        self.position = ab.position

    def data(self):
        gap_val = -1.0  # hodnota kotrou sa ma nahradit '-'

        m = {'A': 0.0, 'C': 1.0, 'G': 2.0, 'T': 3.0, '-': gap_val}
        res = [m[self.base]]
        for i in self.annotations.values():
            if i == '-':
                res.append(gap_val)
            else:
                res.append(float(i))
        return res


class AnnotatedBaseCouple:
    def __init__(self, annotations=None):
        if annotations is None:
            self.annotations = []
        else:
            self.annotations = annotations

        self.X = AnnotatedBase()
        self.Y = AnnotatedBase()

    def data(self):
        return array(list(itertools.chain(*zip(self.X.data, self.Y.data))))

    def is_aligned(self):
        if self.X.base != '-' != self.Y.base:
            return 1
        else:
            return 0


class DataLoader:
    def getSequences(self, fname, sequence_regexp=None):
        alignment_regexp = ""
        if sequence_regexp is None:
            sequence_regexp = ["sequence1$", "sequence2$"]

        #pre zaciatok berieme len prve zarovnanie
        aln = Fasta.load(fname, alignment_regexp, Alignment, sequence_regexp ).next()
        if aln is None or len(aln.sequences) < 2:
            sys.stderr.write("ERROR: not enough sequences in file\n")
            exit(1)
        seq1 = aln.sequences[0]
        seq2 = aln.sequences[1]
        return seq1, seq2

    def loadSequence(self, fname, configFname=None):
        """
        Loads sequence with from file 'fname'
        """
        if configFname is None:
            configFname = path.splitext(fname)[0]
            configFname += '.js'

        seqX, seqY = self.getSequences(fname)
        al = AnnotationLoader()
        annotations, annotationsX, annotationsY = al.get_annotations(configFname)
        #return self._SequenceToAnnotatedBaseCoupleList(annotations,
        #                                               seqX, annotationsX,
        #                                               seqY, annotationsY)

        return annotations, seqX, annotationsX, seqY, annotationsY

    def prepareTrainingData(self, sequence_x, annotations_x, sequence_y, annotations_y, window_size = 1):
        train_data = (list(), list())
        dl = DataPreparer(window=window_size)

        sequence_xs = Fasta.alnToSeq(sequence_x)
        sequence_ys = Fasta.alnToSeq(sequence_y)

        pos_x, pos_y = 0, 0

        matched_pos = set()
        for i in range(len(sequence_x)):
            bx, by = sequence_x[i], sequence_y[i]
            if bx != '-':
                pos_x += 1
                continue
            if by != '-':
                pos_y += 1
                continue

            matched_pos.add((pos_x, pos_y))

            d = dl.prepare_data(sequence_xs, pos_x, annotations_x, sequence_ys, pos_y, annotations_y)
            if d is not None:
                train_data[0].append(d)
                train_data[1].append(1)

        seq_size = len(train_data[0])
        for i in range(seq_size):
            x = None
            while x is None:
                x = randint(window_size//2, len(sequence_xs) - 1 - window_size//2)
            y = None
            while y is None or not (x, y) in matched_pos:
                y = randint(window_size//2, len(sequence_ys) - 1 - window_size//2)

            d = clf.prepare_data(sequence_xs, x, annotations_x, sequence_ys, y, annotations_y)
            train_data[0].append(d)
            train_data[1].append(0)

        return train_data

    def loadDirectory(self, dirname):
        sequences = list()
        for fn in listdir(dirname):
            fname = path.join(dirname, fn)
            if path.isfile(fname):
                sequences.append(self.loadSequence(fname))
        return sequences



