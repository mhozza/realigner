from algorithm.LogNum import LogNum
from hmm.HMMLoader import HMMLoader
from hack.RepeatGenerator import RepeatGenerator
from alignment import Fasta
from adapters.TRFDriver import TRFDriver
from collections import defaultdict
from alignment.AlignmentIterator import AlignmentBeamGenerator, \
                                        AlignmentFullGenerator
from tools import perf
import os   
import argparse

def realign(X_name, X, x, dx, Y_name, Y, y, dy, posteriorTable, hmm, 
            positionGenerator=None, mathType=float):

    D = [defaultdict(lambda *_: defaultdict(mathType)) for _ in range(dx + 1)] 
    
    if positionGenerator == None:
        positionGenerator = AlignmentFullGenerator([X, Y])
    
    # compute table
    for (_x, _y)in positionGenerator:
        bestScore = mathType(0.0)
        bestFrom = (-1, -1, -1)
        for ((fr, _sdx, _sdy), prob) in posteriorTable[_x][_y].iteritems():
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
    for (stateID, _dx, _dy) in aln:
        annotation += hmm.states[stateID].getChar() * max(_dx, _dy)
        X_aligned += X[x + _x: x + _x + _dx] + '-' * max (0, _dy - _dx)
        Y_aligned += Y[y + _y: y + _y + _dy] + '-' * max (0, _dx - _dy)
        _x += _dx
        _y += _dy
    return [(X_name, X_aligned),
            ("annotation of " + X_name + " and " + Y_name, annotation),
            (Y_name, Y_aligned)]
    
def getMathType(s):
    if s == 'LogNum':
        return LogNum
    elif s == 'float':
        return float
    else:
        raise('Unknown type')
    
def toList(s):
    return [s]

@perf.runningTimeDecorator
def main():
    
    parser = argparse.ArgumentParser(description='Realign sequence using informations from repeat realigner')
    parser.add_argument('--mathType', '-m', type=getMathType, default=float, choices=[LogNum, float])
    parser.add_argument('alignment', type=str)
    parser.add_argument('output', type=str)
    parser.add_argument('--model', '-M', type=str, default='data/models/repeatHMM.js')
    parser.add_argument('--trf', '-t', type=toList, default=[
                           "/cygdrive/c/cygwin/bin/trf407b.dos.exe",
                           "C:\\cygwin\\bin\\trf407b.dos.exe",
                           "/home/mic/Vyskum/duplikacie/trf404.linux64",
                           "/home/mic/bin/trf404.linux64",
                           ])
    parsed_arg = parser.parse_args()
    mathType = parsed_arg.mathType
    
        
    # Parse input parameters
    alignment_filename = parsed_arg.alignment
    output_filename = parsed_arg.output

    # Load model
    loader = HMMLoader(mathType) 
    model_filename = parsed_arg.model
    #model_filename = "data/models/EditDistanceHMM.js"
    #model_filename = "data/models/SimpleHMM.js"
    
    PHMM = loader.load(model_filename)["model"]

    # Load alignment
    aln = Fasta.load(alignment_filename)
    if len(aln.sequences) < 2:
        print("ERROR: not enough sequences in file")
        
    # Sequence 1
    seq1 = Fasta.alnToSeq(aln.sequences[0])
    seq1_length = len(seq1)
    seq1_name = aln.names[0]
    
    # Sequence 2
    seq2 = Fasta.alnToSeq(aln.sequences[1])
    seq2_length = len(seq2)
    seq2_name = aln.names[1]
    
    perf.msg("Data loaded in {time} seconds.")
    perf.replace()
    
    # Compute repeat hints
    for trf_executable in parsed_arg.trf:
        if os.path.exists(trf_executable):
            trf = TRFDriver(trf_executable, mathType=mathType)
            break
        
    repeats = trf.run(alignment_filename)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    seq1_repeats = repeats[seq1_name]
    seq2_repeats = repeats[seq2_name]
    PHMM.states[PHMM.statenameToID['Repeat']].addRepeatGenerator(
        RepeatGenerator(seq1_repeats),
        RepeatGenerator(seq2_repeats),
    )
    
    # positions
    positionGenerator = \
        AlignmentBeamGenerator(aln, width = 10)
    positionGenerator = list(positionGenerator)
    
    perf.msg("Hints computed in {time} seconds.")
    perf.replace()
    
    # Compute stuff
    table = PHMM.getPosteriorTable(seq1, 0, seq1_length, seq2, 0, seq2_length,
                                   positionGenerator = positionGenerator)
    
    perf.msg("Posterior table computed in {time} seconds.")
    perf.replace()
    
    aln = ""
    aln = realign(
        seq1_name, seq1, 0, seq1_length,
        seq2_name, seq2, 0, seq2_length,
        table,
        PHMM,
        positionGenerator,
        mathType=mathType
    )
    
    perf.msg("Sequence was realigned in {time} seconds.")
    perf.replace()
    
    # Save output
    Fasta.save(aln, output_filename)
    perf.msg("Output saved in {time} seconds.")

    
if __name__ == "__main__":
    main()
    perf.printAll()
    