import argparse
from alignment.Fasta import loadGenerator
from collections import defaultdict
import json
    
    
def getType(pair):
    x, y = pair
    if x == '-' and y != '-':
        return 'Y'
    if y == '-' and x != '-':
        return 'X'
    if x != '-' and y != '-':
        return 'M'
    print pair
    assert(False)


def skip(p):
    if 'N' in p or 'n' in p or '-' in p:
        return True
    return False


def upper(p):
    return tuple([x.upper() for x in p])

def sortTypes(types):
    buff = []
    for x in types:
        if x == 'M':
            #buff.sort()
            for y in buff:
                yield y
            buff = [] 
            yield x
        buff.append(x)
    #buff.sort()
    for x in buff:
        yield x
        

def main(input_file, index1, index2, emissionOutput, transitionOutput):
    
    emissions = defaultdict(int)
    transitions = defaultdict(int)
    
    count = 0
    last = ''
    X = None
    Y = None
    
    def aggregate(X, Y):
        pairs = zip(X, Y)
        for p in pairs:
            if skip(p):
                continue
            emissions[str(upper(p))] += 1
        Types = list(sortTypes([getType(x) for x in pairs if x != ('-', '-')]))
        for p in zip(Types, Types[1:]):
            transitions[str(p)] += 1
    
    for seq_name, sequence in loadGenerator(input_file):
        a = seq_name.split('.')
        if a[-1] != last:
            if X != None and Y != None:
                aggregate(X, Y)
            X, Y = None, None
            count = 0
            last = a[-1]
        if count == index1:
            X = sequence
        if count == index2:
            Y = sequence
        count += 1
    if X != None and Y != None:
        aggregate(X, Y)
        
    with open(emissionOutput, 'w') as f:
        json.dump(emissions, f, indent=4)
        
    with open(transitionOutput, 'w') as f:
        json.dump(transitions, f, indent=4)


if __name__ == '__name__':
    parser = argparse.ArgumentParser(description='Aggregate statistics from alignment.')
    parser.add_argument('input', type=str, help='Program input -- alignment')
    parser.add_argument('index1', type=int, help='First row of alignment to compare')
    parser.add_argument('index2', type=int, help='First row of alignment to compare')
    parser.add_argument('emissionOutput', type=str, help='Output file')
    parser.add_argument('transitionOutput', type=str, help='Output file')
    parsed_arg = parser.parse_args()
    main(
         parsed_arg.input,
         parsed_arg.index1,
         parsed_arg.index2,
         parsed_arg.emissionOutput,
         parsed_arg.transitionOutout
    )