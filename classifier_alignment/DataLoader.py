"""
Created on May 10, 2013

@author: Michal Hozza
"""
from alignment import Fasta
from alignment.Alignment import Alignment
from os import path, listdir
from tools.Exceptions import ParseException
from classifier_alignment.AnnotationLoader import AnnotationLoader


class DataLoader:
    def getSequences(self, fname, sequence_regexp=None):
        alignment_regexp = ''
        if sequence_regexp is None:
            sequence_regexp = ["^sequence1$", "^sequence2$"]
        self.sequence_regexp = sequence_regexp
        aln = next(
            Fasta.load(fname, alignment_regexp, Alignment, sequence_regexp)
        )
        if aln is None or len(aln.sequences) < 2:
            raise ParseException('Not enough sequences in file\n')
        seq1 = aln.sequences[0]
        seq2 = aln.sequences[1]
        return seq1, seq2

    @staticmethod
    def default_annotation_fname(fname):
        return path.splitext(fname)[0] + '.js'

    def loadSequence(self, fname, configFname=None):
        """
        Loads sequence with from file 'fname'
        """
        if configFname is None:
            configFname = DataLoader.default_annotation_fname(fname)

        seqX, seqY = self.getSequences(fname)
        al = AnnotationLoader(self.sequence_regexp)
        annotations, annotationsX, annotationsY = al.get_annotations(
            configFname
        )

        return annotations, seqX, annotationsX, seqY, annotationsY

    def loadDirectory(self, dirname):
        sequences = list()
        for fn in filter(
            lambda x: path.splitext(x)[1] == '.fa', listdir(dirname)
        ):
            fname = path.join(dirname, fn)
            if path.isfile(fname):
                sequences.append(self.loadSequence(fname))
        return sequences
