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
        posX = 0
        posY = 0
        for i in range(len(seqX)):
            b = AnnotatedBaseCouple(annotations)
            b.X.base = seqX[i]            
            b.X.position = posX;
            b.X.annotations = self.getAnnotationsAt(annotationsX, posX)
            b.Y.base = seqY[i]
            b.X.position = posY;
            b.Y.annotations = self.getAnnotationsAt(annotationsY, posX)

            if(b.X.base!='-'):
                posX+=1
            if(b.Y.base!='-'):
                posY+=1
            data.append(b)
        return data


    def _getAnnotations_old(self, fname):
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
    
    def _intervalsToIntervalMap(self, intervals):
        '''
        Converts intervals from track to intervalmap, for searching
                
        currently supports binary annotations only
        '''
        m = intervalmap()        
        m[:] = 0
        for i in intervals:
            m[i['start']:i['end']] = 1
        return m
    
    
    def _getAnnotationFromBED(self, fname):
        '''
        Reads intervals from BED file
        '''  
        with track.load(fname) as ann:
            ann = ann.read()
        return self._intervalsToIntervalMap(ann)
    
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
            configFname, ext = path.splitext(fname)
            configFname+='.js'
        
        seqX, seqY = self.getSequences(fname)
        annotations, annotationsX, annotationsY = self.getAnnotations(configFname)
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
            x = None
            while x == None or abcList[x].X.base == '-':
                x = (randint(0,seq_size-1))
            y = None
            while y == None or y==x or abcList[y].Y.base == '-' :
                y = (randint(0,seq_size-1))
            
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


    