'''
Created on Jan 17, 2013

@author: mic
'''
from alignment.Realigner import Realigner
from repeats.RepeatGenerator import RepeatGenerator
from collections import defaultdict
from alignment.AlignmentIterator import AlignmentFullGenerator, \
                                        AlignmentPositionGenerator
import json
from algorithm.LogNum import LogNum
from tools import perf
from tools.file_wrapper import Open

def jsonize(inp):
    t = type(inp)
    if t == dict or t == defaultdict:
        output = dict()
        for k, v in inp.iteritems():
            output[str(k)] = jsonize(v)
        return output
    elif t == list:
        output = []
        for x in inp:
            output.append(jsonize(x))
        return output
    elif t == type(LogNum()):
        return inp.value
    return inp

def divide(table, probability):
    if type(table) == list:
        return [divide(x, probability) for x in table]
    elif type(table) == dict or type(table) == defaultdict:
        for k, v in table.iteritems():
            table[k] = divide(v, probability)
    else:
        return table / probability
    return table

def strtokey(x):
    x = x.strip('()')
    a = [int(l) for l in x.split(',')]
    if len(a) == 1:
        return a[0]
    return tuple(a)
                            
def dejsonize(inp, mathType=float):
    if type(inp) == dict or type(inp) == defaultdict:
        out = defaultdict(lambda *x: defaultdict(mathType))
        for k, v in inp.iteritems():
            out[strtokey(k)] = dejsonize(v)
        return out
    elif type(inp) == list:
        return map(dejsonize, inp)
    else:
        if mathType != float:
            return mathType(inp, log=False)
        else:
            return inp


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
    def prepareData(self, *data):
        data = Realigner.prepareData(self, *data)
        arguments = 0
        
        # Add repeats
        for (rt, ch) in [('trf', 'R'), ('original_repeats', 'r')]:
            if rt in self.annotations:
                self.model.states[
                    self.model.statenameToID['Repeat']
                ].addRepeatGenerator(
                    RepeatGenerator(self.annotations[rt][self.X_name],
                                    self.repeat_width),
                    RepeatGenerator(self.annotations[rt][self.Y_name],
                                    self.repeat_width),
                )
                self.drawer.add_repeat_finder_annotation(
                    'X', ch, self.annotations[rt][self.X_name], 
                    (255, 0, 0, 255))
                self.drawer.add_repeat_finder_annotation(
                    'Y', ch, self.annotations[rt][self.Y_name],
                    (255, 0, 0, 255))

        #posterior table
        #position generator
        
        if 'posterior' not in self.io_files['input']:
            self.posteriorTable, probability = self.model.getPosteriorTable(
                self.X, 0, len(self.X),
                self.Y, 0, len(self.Y),
                positionGenerator=self.positionGenerator
            )
            
            self.posteriorTable = divide(self.posteriorTable, probability)
            self.drawer.add_posterior_table(self.posteriorTable)
            
            x = jsonize(self.posteriorTable)
            if 'posterior' in self.io_files['output']:
                with Open(self.io_files['output']['posterior'], 'w') as f:
                    json.dump(x, f,indent=4)
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
        perf.msg("Posterior table computed in {time} seconds.")
        perf.replace()
                
        return data[arguments:]

    
    #TODO: vymysli datovy model pre rozne tracky, refaktoruj
    #TODO: mio: refaktoruj to pre tento datovy model -- ty ho potrebujes
    #TODO: sklearn ma nejake HMMka v sebe. Mozno by sme chceli porozmyslat ci 
    #      nechceme byt kompatibilny s nimi   
    def realign(self, x, dx, y, dy, ignore=set(), positionGenerator=None):
        """Realign part of sequences."""
        # TODO: split this into multiple function
        
        D = [
            defaultdict(lambda *_: (self.mathType(0.0), (-1, -1, -1)))
            for _ in range(dx + 1)
        ] 
        if positionGenerator == None:
            if self.positionGenerator != None:
                positionGenerator = self.positionGenerator
            else:
                positionGenerator = AlignmentFullGenerator([self.X, self.Y]) 
        # compute table
        for (_x, _y)in positionGenerator:
            bestScore = self.mathType(0.0)
            bestFrom = (-1, -1, -1)
            for ((fr, _sdx, _sdy), prob) in \
                self.posteriorTable[x + _x][y + _y].iteritems():
                if fr in ignore:
                    continue
                if _x - _sdx < 0 or _y - _sdy < 0:
                    continue
                sc = D[_x - _sdx][_y - _sdy][0] + \
                    (self.mathType(_sdx + _sdy) * \
                    prob )
                if sc >= bestScore:
                    bestScore = sc
                    bestFrom = (fr, _sdx, _sdy)
            D[_x][_y] = (bestScore, bestFrom)
        # backtrack
        _x = dx
        _y = dy
        aln = []
        while _x > 0 or _y > 0:
            (_, (fr, _dx, _dy)) = D[_x][_y]
            aln.append((fr, _dx, _dy))
            assert(_dx >= 0 and _dy >= 0)
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
