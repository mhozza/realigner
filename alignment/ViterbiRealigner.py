import json
from repeats.RepeatGenerator import RepeatGenerator
from collections import defaultdict
from alignment.Realigner import Realigner
from algorithm.LogNum import LogNum
from tools.file_wrapper import Open
from itertools import cycle

def jsonize(inp):
    t = type(inp)
    if t == type(dict()) or t == type(defaultdict()):
        output = dict()
        for k, v in inp.iteritems():
            output[str(k)] = jsonize(v)
        return output
    elif t == type(list()):
        output = []
        for x in inp:
            output.append(jsonize(x))
        return output
    elif t == type(tuple()):
        output = []
        for x in inp:
            output.append(jsonize(x))
        return tuple(output)
    elif t == type(LogNum()):
        return inp.value
    return inp



def dejsonize(inp, converter):
    if converter != tuple:
        return converter(inp)
    if len(converter) == 0:
        return inp 
    if len(converter) == 1:
        return converter[0](inp)
    tp = converter[0]
    if tp in (list, tuple) and len(converter) == 2:
        return tp([dejsonize(x, converter[1]) for x in inp])
    elif tp in [dict, defaultdict]:
        key = converter[1]
        value = lambda x: x
        if len(converter) > 2:
            value = converter[2]
        return dict([(dejsonize(k, key), dejsonize(v, value))
                     for k, v in inp.iteritems()])
    elif tp in [list, tuple]:
        return tp([
            dejsonize(x, tt) for tt in zip(inp, cycle(converter[1:])) 
        ])
    else:
        raise 'Unknown type:' + str(tp)


class ViterbiRealigner(Realigner):
    def __init__(self):
        self.table = None
        return
   
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
                
        if 'viterbi' not in self.io_files['input']:
            self.table = self.model.getViterbiTable(
                self.X, 0, len(self.X),
                self.Y, 0, len(self.Y),
                positionGenerator=self.positionGenerator
            )
            x = jsonize(self.table)
            if 'viterbi' in self.io_files['output']:
                with Open(self.io_files['output']['viterbi'], 'w') as f:
                    json.dump(x, f,indent=4)
        else:
            self.table = dejsonize(
                json.load(Open(self.io_files['input']['viterbi'])),
                (
                    list,
                    (
                        dict,
                        int,
                        (
                            dict,
                            (tuple, int),
                            (
                                tuple,
                                lambda x: LogNum(x, False),
                                int)))))
        return data[arguments:]

 
    def realing(self, x, dx, y, dy):
        if 'viterbi_path' not in self.io_files['input']:
            path = self.model.getViterbiPath(self.table)
            if 'viterbi_path' in self.io_files['output']:
                with Open(self.io_files['output']['viterbi_path.js'], 'w') as f:
                    json.dump(jsonize(path), f, indent=4)
        else:
            path = dejsonize(
                json.load(Open(self.io_files['input']['viterbi_path'])),
                (
                    list,
                    (
                        tuple,
                        int,
                        (tuple, int),
                        (tuple, int),
                        lambda x: LogNum(x, False))))
        
        X = ""
        Y = ""
        A = ""
            
        for (state, (_x, _y), (_dx, _dy), _) in path:
            X += self.X[_x - _dx:_x] + ('-' * (_dx - max(_dx, _dy)))
            Y += self.Y[_y - _dy:_y] + ('-' * (_dy - max(_dx, _dy)))
            A += self.model.states[state].getChar() * max(_dx, _dy)
            
        return [(self.X_name, X), ("viterbi annotation of " + self.X_name + 
                                   " and " + self.Y_name, A),
                (self.Y_name, Y)]
