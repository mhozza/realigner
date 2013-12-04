'''
Created on Jan 17, 2013

@author: mic
'''
from alignment.Realigner import Realigner
from collections import defaultdict
from alignment.AlignmentIterator import AlignmentFullGenerator, \
                                        AlignmentPositionGenerator
import json
from tools import perf
from tools.file_wrapper import Open
from tools.debug import jsonize, dejsonize


def divide(table, probability):
    if type(table) == list:
        return [divide(x, probability) for x in table]
    elif type(table) == dict or type(table) == defaultdict:
        for k, v in table.iteritems():
            table[k] = divide(v, probability)
    else:
        return table / probability
    return table


class RepeatRealigner(Realigner):
    '''
    classdocs
    '''
    
    def __init__(self):
        """
        Constructor
        """
        self.posteriorTable = None
   
    @perf.runningTimeDecorator
    def marginalizeGaps(self, table):
        gapdict = defaultdict(lambda *_: self.mathType(0.0))
        for i in range(len(table)):
            for j, D in table[i].iteritems():
                for (s, x, y), p in D.iteritems():
                    if x != 0 and y != 0:
                        continue
                    if x == 0 and y == 0:
                        continue
                    if x == 0:
                        y = j
                    if y == 0:
                        x = i
                    gapdict[(s, x, y)] += p
        for i in range(len(table)):
            for j, D in table[i].iteritems():
                for (s, x, y), p in D.iteritems():
                    if x != 0 and y != 0:
                        continue
                    if x == 0 and y == 0:
                        continue
                    nx = 0
                    ny = 0
                    if x == 0:
                        ny = j
                    if y == 0:
                        nx = i
                    #table[i][j][(s, x, y)] = gapdict[(s, x, y)]
                    table[i][j][(s, x, y)] = gapdict[(s, nx, ny)]
        return table


    @perf.runningTimeDecorator
    def applyAnnotation(self, table, annotation):
        new = [defaultdict(
            lambda *_: defaultdict(lambda *_: self.mathType(0.0))
        ) for _ in range(len(table))]
        for i in range(len(table)):
            for j, D in table[i].iteritems():
                for (s, x, y), p in D.iteritems():
                    new[i][j][(annotation[s], x, y)] += p
        return new


    @perf.runningTimeDecorator
    def oneCharAnnotation(self):
        annotation = []
        d = dict()
        for i in range(len(self.model.states)):
            nm = self.model.states[i].stateName
            if nm == 'InsertX':
                c = 'X'
            elif nm == 'InsertY':
                c = 'T'
            else:
                c = nm[0]
            if c not in d:
                d[c] = i
            ind = d[c]
            annotation.append(ind)
        return annotation
    
      
    @perf.runningTimeDecorator
    def computePosterior(self):
        if 'posterior' not in self.io_files['input']:
            self.posteriorTable, probability = self.model.getPosteriorTable(
                self.X, 0, len(self.X),
                self.Y, 0, len(self.Y),
                positionGenerator=self.positionGenerator,
            )
            self.posteriorTable = divide(self.posteriorTable, probability)
            x = jsonize(self.posteriorTable)
            if 'posterior' in self.io_files['output']:
                with Open(self.io_files['output']['posterior'], 'w') as f:
                    json.dump(x, f, indent=4, sort_keys=True)
        else:
            with open(self.io_files['input']['posterior'], 'r') as f:
                self.posteriorTable = dejsonize(json.load(f), self.mathType)
        self.drawer.add_borders_line(
            100,
            (0, 255, 255, 255),
            1,
            self.positionGenerator
        )
        self.drawer.add_alignment_line(
            100,
            (0, 255, 255, 255),
            1,
            list(AlignmentPositionGenerator(self.alignment))
        )


    @perf.runningTimeDecorator
    def prepareData(self, *data):
        data = Realigner.prepareData(self, *data)
        arguments = 0
       
        self.computePosterior()       
        return data[arguments:]

    
    #TODO: vymysli datovy model pre rozne tracky, refaktoruj
    #TODO: sklearn ma nejake HMMka v sebe. Mozno by sme chceli porozmyslat ci 
    #      nechceme byt kompatibilny s nimi   
    def realign(self, x, dx, y, dy, ignore=set(), positionGenerator=None):
        """Realign part of sequences."""
        # TODO: split this into multiple function
        if self.one_char_annotation:
            annotation = self.oneCharAnnotation()
            self.posteriorTable = self.applyAnnotation(
                self.posteriorTable,
                annotation
            )
        if self.marginalize_gaps:
            self.posteriorTable = self.marginalizeGaps(self.posteriorTable)

        if positionGenerator == None:
            if self.positionGenerator != None:
                positionGenerator = self.positionGenerator
            else:
                positionGenerator = AlignmentFullGenerator([self.X, self.Y])

        D = self.computeBacktrackTable(x, dx, y, positionGenerator, ignore)
        
        aln = self.backtrack(dx, dy, D)
        return self.generateAnnotationAndAlignment(
            aln,
            x,
            y,
            positionGenerator,
            ignore,
        )


    @perf.runningTimeDecorator
    def computeBacktrackTable(self, x, dx, y, positionGenerator, ignore):
        D = [defaultdict(lambda*_:(self.mathType(0.0), (-1, -1, -1))) for 
            _ in range(dx + 1)]
        one_math = self.mathType(1.0)
        for _x, _y in positionGenerator:
            bestScore = self.mathType(0.0)
            bestFrom = -1, -1, -1
            something = False
            it = self.posteriorTable[x + _x][y + _y].iteritems()
            for (fr, _sdx, _sdy), prob in it:
                if fr in ignore:
                    continue
                if _x - _sdx < 0 or _y - _sdy < 0:
                    continue
                mult = self.mathType(_sdx + _sdy)
                if self.posterior_score:
                    mult = one_math
                sc = D[_x - _sdx][_y - _sdy][0] + (
                    mult * prob
                )
                if sc >= bestScore or (not something):
                    bestScore = sc
                    bestFrom = fr, _sdx, _sdy
                    something = True
            
            D[_x][_y] = bestScore, bestFrom
        
        #print 'BackTrack {} {} {} {} {} {}'.format(x, dx, y, dy, ignore, positionGenerator)
        return D


    @perf.runningTimeDecorator
    def backtrack(self, dx, dy, D):
        # backtrack
        _x = dx
        _y = dy
        aln = []
        #from tools.debug import jbug
        #jbug(self.posteriorTable, 'Posterior table')
        #jbug(D, 'D')
        while _x > 0 or _y > 0:
            (_, (fr, _dx, _dy)) = D[_x][_y]
            aln.append((fr, _dx, _dy))
            #print _x, _y, _dx, _dy
            assert(_dx >= 0 and _dy >= 0)
            _x -= _dx
            _y -= _dy             
        aln = list(reversed(aln))
        return aln
    
    
    @perf.runningTimeDecorator
    def generateAnnotationAndAlignment(
        self,
        aln,
        x,
        y,
        positionGenerator,
        ignore,
    ):
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
                      positionGenerator[index][0] <= window[0][1] and \
                      (
                          positionGenerator[index][0] < window[0][1] or \
                          positionGenerator[index][1] <= window[1][1] \
                      ):
                    if window[0][0] <= positionGenerator[index][0] and \
                       positionGenerator[index][0] <= window[0][1] and \
                       window[1][0] <= positionGenerator[index][1] and \
                       positionGenerator[index][1] <= window[1][1]:
                        pG.append((positionGenerator[index][0] - window[0][0], 
                                   positionGenerator[index][1] - window[1][0]))
                    index += 1
                ign = set(ignore)
                ign.add(stateID)
                rr = self.realign(x + _x, _dx, y + _y, _dy, ign, pG)
                X_aligned += rr[0][1]
                Y_aligned += rr[2][1]
                annotation += (self.model.states[stateID].getChar() * 
                               len(rr[0][1]))
            else: 
                X_aligned += self.X[x + _x: x + _x + _dx] + '-' * max(0,
                                                                      _dy - _dx)
                Y_aligned += self.Y[y + _y: y + _y + _dy] + '-' * max(0,
                                                                      _dx - _dy)
                annotation += self.model.states[stateID].getChar() * alnPartLen
            _x += _dx
            _y += _dy
        return [(self.X_name, X_aligned),
                ("annotation of " + self.X_name + " and " + self.Y_name, 
                 annotation),
                (self.Y_name, Y_aligned)]
