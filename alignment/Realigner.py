# coding=utf-8
'''
Created on Jan 17, 2013

@author: Michal Nánási (michal.nanasi@gmail.com)
'''

from collections import defaultdict
from alignment.AlignmentIterator import AlignmentFullGenerator

class Realigner(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def prepareData(self, *data):
        pass
    
    #TODO: vymysli datovy model pre rozne tracky, refaktoruj
    #TODO: mio: refaktoruj to pre tento datovy model -- ty ho potrebujes
    #TODO: sklearn ma nejake HMMka v sebe. Mozno by sme chceli porozmyslat ci nechceme
    #      byt kompatibilny s nimi   
    def realign(self, X_name, X, x, dx, Y_name, Y, y, dy, posteriorTable, hmm, 
            positionGenerator=None, mathType=float, ignore=set()):
        
        D = [defaultdict(lambda *_: defaultdict(mathType)) for _ in range(dx + 1)] 
    
        if positionGenerator == None:
            positionGenerator = AlignmentFullGenerator([X, Y]) #BUG!!! -- indexy nesedia
        
        # compute table
        for (_x, _y)in positionGenerator:
            bestScore = mathType(0.0)
            bestFrom = (-1, -1, -1)
            for ((fr, _sdx, _sdy), prob) in posteriorTable[_x][_y].iteritems():
                if fr in ignore:
                    continue
                sc = D[_x - _sdx][_y - _sdy][0] + mathType(_sdx + _sdy) * prob
                if sc >= bestScore:
                    bestScore = sc
                    bestFrom = (fr, _sdx, _sdy)
            #if bestScore >= 0:
            D[_x][_y] = (bestScore, bestFrom)
        # backtrack
        _x = dx
        _y = dy
        aln = []
        while _x > 0 or _y > 0:
            (_, (fr, _dx, _dy)) = D[_x][_y]
            aln.append((fr, _dx, _dy))
            _x -= _dx
            _y -= _dy             
        aln = list(reversed(aln))
        #generate annotation and alignment
        X_aligned = ""
        Y_aligned = ""
        annotation = ""
        _x = 0
        _y = 0
        index = 0
        for (stateID, _dx, _dy) in aln:
            alnPartLen = max(_dx, _dy)
            if alnPartLen > 1:
                window = ( (x + _x, x + _x + _dx),
                           (y + _y, y + _y + _dy))
                pG = list()
                while index < len(positionGenerator) and \
                      positionGenerator[index][0] <= window[0][1]:
                    if window[0][0] <= positionGenerator[index][0] and \
                       positionGenerator[index][0] <= window[0][1] and \
                       window[1][0] <= positionGenerator[index][1] and \
                       positionGenerator[index][1] <= window[1][1]:
                        pG.append((positionGenerator[index][0] - window[0][0],
                                   positionGenerator[index][1] - window[1][0]))
                    index += 1
                ign = set(ignore)
                ign.add(stateID)
                rr = self.realign(X_name, X, x + _x, _dx, Y_name, Y, y + _y, _dy, 
                             posteriorTable, hmm, pG, mathType, ign)
                X_aligned += rr[0][1]
                Y_aligned += rr[2][1]
                annotation += hmm.states[stateID].getChar() * len(rr[0][1])
            else: 
                X_aligned += X[x + _x: x + _x + _dx] + '-' * max (0, _dy - _dx)
                Y_aligned += Y[y + _y: y + _y + _dy] + '-' * max (0, _dx - _dy)
                annotation += hmm.states[stateID].getChar() * alnPartLen
            _x += _dx
            _y += _dy
        return [(X_name, X_aligned),
                ("annotation of " + X_name + " and " + Y_name, annotation),
                (Y_name, Y_aligned)]