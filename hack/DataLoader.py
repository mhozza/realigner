'''
Created on May 10, 2013

@author: Michal Hozza
'''
from alignment import Fasta
from alignment.Alignment import Alignment
from copy import deepcopy
import hmm.HMMLoader
from numpy import array
from os import path, listdir
from random import randint
from tools.intervalmap import intervalmap
import itertools
import sys
import track


class AnnotatedBase:
    def __init__(self):
        self.base = '-'
        self.annotations = {}
        self.position = 0

    def copy(self, ab):
        self.base = ab.base
        self.annotations = deepcopy(ab.annotations)
        self.position = ab.position

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


class DataLoader:
    def getAnnotationsAt(self, annotations, i):
        '''
        Returns annotations at position i
        '''
        baseAnnotation = dict()
        if annotations != None:
            for key in annotations:
                baseAnnotation[key] = annotations[key][i]
        return baseAnnotation

#    def alnToAnnotation(self, annotations):
#        newannotations = dict()
#        for key in annotations:
#            newannotations[key] =  annotations[key].replace("-","")
#        return newannotations

    def _SequenceToAnnotatedBaseCoupleList(self, annotations, seqX, annotationsX,
                                           seqY, annotationsY):
        if len(seqX) != len(seqY):
            print(seqX)
            print(seqY)
            sys.stderr.write("ERROR: sequences does not have same length\n")
            exit(1)

        data = list()
        posX = 0
        posY = 0
        for i in range(len(seqX)):
            b = AnnotatedBaseCouple(annotations)
            b.X.base = seqX[i]
            b.X.position = posX;
            b.X.annotations = self.getAnnotationsAt(annotationsX, posX)
            b.Y.base = seqY[i]
            b.X.position = posY;
            b.Y.annotations = self.getAnnotationsAt(annotationsY, posY)

            if(b.X.base!='-'):
                posX+=1
            if(b.Y.base!='-'):
                posY+=1
            data.append(b)
        return data

    def _intervalsToIntervalMap(self, intervals):
        '''
        Converts intervals from track to intervalmap, for searching

        currently supports binary annotations only
        '''
        m = intervalmap()
        m[:] = 0
        for i in intervals:
            m[i[1]:i[2]] = 1
        return m

    def _getAnnotationFromBED(self, fname):
        '''
        Reads intervals from BED file
        '''
        try:
            with track.load(fname) as ann:
                ann = ann.read(fields=['start', 'end'])
                intervals = self._intervalsToIntervalMap(ann)
        except Exception:
            intervals = self._intervalsToIntervalMap([])
        return intervals

    def _getSequenceAnnotations(self, annotations, sequenceAnnotationsConfig):
        '''
        Returns annotations for one sequence
        '''
        res = dict()
        for annotation in annotations:
            res[annotation] = self._getAnnotationFromBED(sequenceAnnotationsConfig[annotation])
        return res


    def getAnnotations(self, fname):
        loader = hmm.HMMLoader.HMMLoader()
        annotationConfig = loader.load(fname)
        annotations = annotationConfig.annotations
        annotationsX =  self._getSequenceAnnotations(annotations, annotationConfig.sequences["sequence1"])
        annotationsY =  self._getSequenceAnnotations(annotations, annotationConfig.sequences["sequence2"])
        return annotations, annotationsX, annotationsY


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


    def loadSequence(self, fname, configFname=None):
        '''
        Loads sequence with from file 'fname'
        '''
        if configFname==None:
            configFname = path.splitext(fname)[0]
            configFname+='.js'

        seqX, seqY = self.getSequences(fname)
        annotations, annotationsX, annotationsY = self.getAnnotations(configFname)
        return self._SequenceToAnnotatedBaseCoupleList(annotations,
                                                       seqX, annotationsX,
                                                       seqY, annotationsY)



    def _checkWindowX(self, abcList, index, size = 1):
        for i in range(index-size//2,index+(1+size)//2):
            if i>=len(abcList) or i<0:
                return False
            if abcList[i].X.base == '-':
                return False
        return True

    def _checkWindowY(self, abcList, index, size = 1):
        for i in range(index-size//2,index+(1+size)//2):
            if i>=len(abcList) or i<0:
                return False
            if abcList[i].Y.base == '-':
                return False
        return True

    def _createXYWindow(self, abcList, indexX, indexY, size = 1):
        l = list()
        for i in range(size):
            b = AnnotatedBaseCouple(abcList[0].annotations)
            b.X = abcList[i+indexX-size//2].X
            b.Y = abcList[i+indexY-size//2].Y
            l+=list(b.toTrainData())
        return array(l)

    def _createDataWindow(self, abcList, index, size = 1):
        l = list()
        for i in range(index-size//2,index+(1+size)//2):
            if i>=len(abcList) or i<0:
                return None
            item = abcList[i]
            if not item.isAligned():
                return None
            l+=list(item.toTrainData())
        return array(l)

    def prepareTrainingData(self, abcList, windowSize = 1):
        train_data = (list(), list())
        for i in range(len(abcList)):
            w = self._createDataWindow(abcList, i, windowSize)
            if w!=None:
                train_data[0].append(w)
                train_data[1].append(1)

        seq_size = len(train_data[0])
        for i in range(seq_size):
            x = None
            while x == None or not self._checkWindowX(abcList, x, windowSize):
                x = randint(0,seq_size-1)
            y = None
            while y == None or not self._checkWindowY(abcList, y, windowSize):
                y = randint(0,seq_size-1)

            w = self._createXYWindow(abcList, x, y, windowSize)
            train_data[0].append(w)
            train_data[1].append(0)

        return train_data

    def loadDirectory(self, dirname):
        sequences = list()
        for fn in listdir(dirname):
            fname = path.join(dirname, fn)
            if path.isfile(fname):
                sequences.append(self.loadSequence(fname))
        return sequences


