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
        self.marginalize_gaps = False
        self.one_char_annotation = False
        self.args = None
        '''
        Constructor
        '''
    
    def prepareData(self, *data):
        """Push data to realing. Including sequence. Precompute stuff you 
        need"""
        arguments = 8
        (self.X, self.X_name, self.Y, self.Y_name, self.alignment,
         self.model, self.annotations, self.args) = tuple(data[:arguments])
         
        self.width = self.args.beam_width
        self.mathType = self.args.mathType
        self.io_files = {
            'input': self.args.intermediate_input_files,
            'output': self.args.intermediate_output_files
        }
        self.repeat_width = self.args.repeat_width
        self.cons_count = self.args.cons_count
        self.marginalize_gaps = self.args.marginalize_gaps
        self.one_char_annotation = self.args.one_char_annotation 

        self.positionGenerator = \
            list(AlignmentBeamGenerator(self.alignment, self.width))
         
        for i in range(len(self.model.states)):
            self.model.states[i].computeHints(self)

        return data[arguments:]
    
    def setDrawer(self, drawer):
        self.drawer = drawer

    def realign(self, x, dx, y, dy, ignore=set()):
        """Realign part of sequences."""
        return ['', '', '']
