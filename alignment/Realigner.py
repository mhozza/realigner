# coding=utf-8
'''
Created on Jan 17, 2013

@author: Michal Nánási (michal.nanasi@gmail.com)
'''
from alignment.AlignmentIterator import AlignmentBeamGenerator


class Realigner(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.X = None
        self.Y = None
        self.X_name = None
        self.Y_name = None
        self.alignment = None
        self.drawer = None
        self.width = None
        self.model = None
        self.mathType = None
        self.annotations = None
        self.io_files = None
        self.positionGenerator = None
        self.repeat_width = None
        self.cons_count = None
        self.merge_consensus = False
        self.correctly_merge_consensus = False
        self.ignore_consensus = False
        '''
        Constructor
        '''
    
    def prepareData(self, *data):
        """Push data to realing. Including sequence. Precompute stuff you 
        need"""
        arguments = 16
        (self.X, self.X_name, self.Y, self.Y_name, self.alignment, self.width,
         self.drawer, self.model, self.mathType, self.annotations,
         self.io_files, self.repeat_width, self.cons_count, self.merge_consensus, self.correctly_merge_consensus, self.ignore_consensus) = tuple(data[:arguments])
        self.positionGenerator = \
            list(AlignmentBeamGenerator(self.alignment, self.width))
        if 'Repeat' in self.model.statenameToID:
            self.model.states[self.model.statenameToID['Repeat']].merge_consensus = self.merge_consensus
            self.model.states[self.model.statenameToID['Repeat']].correctly_merge_consensus = self.correctly_merge_consensus
        return data[arguments:]
    

    def realign(self, x, dx, y, dy, ignore=set()):
        """Realign part of sequences."""
        return ['', '', '']
