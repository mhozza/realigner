from algorithm.LogNum import LogNum
from collections import defaultdict
from itertools import cycle
from tools.file_wrapper import Open

import json


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

def jsonize_to_list(inp):
    t = type(inp)
    if t == dict or t == defaultdict:
        output = list()
        for k, v in inp.iteritems():
            output.append((jsonize_to_list(k), jsonize_to_list(v)))
        return output
    elif t == list:
        output = []
        for x in inp:
            output.append(jsonize_to_list(x))
        return output
    elif t == type(LogNum()):
        return inp.value
    elif t == tuple:
        output = []
        for x in inp:
            output.append(jsonize_to_list(x))
        return tuple(output)
    return inp


def dejsonize_struct(inp, converter):
    if converter != tuple:
        return converter(inp)
    if len(converter) == 0:
        return inp 
    if len(converter) == 1:
        return converter[0](inp)
    tp = converter[0]
    if tp in (list, tuple) and len(converter) == 2:
        return tp([dejsonize_struct(x, converter[1]) for x in inp])
    elif tp in [dict, defaultdict]:
        key = converter[1]
        value = lambda x: x
        if len(converter) > 2:
            value = converter[2]
        return dict([(dejsonize_struct(k, key), dejsonize_struct(v, value))
                     for k, v in inp.iteritems()])
    elif tp in [list, tuple]:
        return tp([
            dejsonize_struct(x, tt) for tt in zip(inp, cycle(converter[1:])) 
        ])
    else:
        raise 'Unknown type:' + str(tp)
    
    
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


def jbug(structure, text=None, filename=None):
    dump = json.dumps(jsonize(structure), sort_keys=True, indent=4)
    if filename:
        with Open(filename, 'w') as f:
            f.write(dump)
    else:          
        print text + ': ' + dump