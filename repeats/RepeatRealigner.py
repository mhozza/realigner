'''
Created on Jan 17, 2013

@author: mic
'''
from alignment.Realigner import Realigner
from repeats.RepeatGenerator import RepeatGenerator

class RepeatRealigner(Realigner):
    '''
    classdocs
    '''
    
    def prepareData(self, *data):
        PHMM, seq1_repeats, seq2_repeats = tuple(data)
        PHMM.states[PHMM.statenameToID['Repeat']].addRepeatGenerator(
            RepeatGenerator(seq1_repeats),
            RepeatGenerator(seq2_repeats),
        )

    def __init__(self):
        '''
        Constructor
        '''
        