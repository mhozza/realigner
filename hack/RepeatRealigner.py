import AlignmentIterator
from LogNum import LogNum
import sys
from HMMLoader import HMMLoader
from RepeatGenerator import RepeatGenerator
import Fasta
from TRFDriver import TRFDriver
from collections import defaultdict
from tools import structtools
import profile
import os

def realign(X_name, X, x, dx, Y_name, Y, y, dy, posteriorTable, hmm):

    # [x][y][(state, dx, dy)]
    #f = open("debug.txt", "w")
    #f.write(structtools.structToStr(posteriorTable, 3, ""))
    #f.close()
    D = [defaultdict(lambda *_: defaultdict(float)) for _ in range(dx + 1)] # [x]{y} = (score, (fromstate, dx, dy))
    
    # compute table
    for _x in range( dx + 1):
        for (_y, _) in \
                posteriorTable[_x].iteritems():
            bestScore = -1.0
            bestFrom = (-1, -1, -1)
            for ((fr, _sdx, _sdy), prob) in posteriorTable[_x][_y].iteritems():
                sc = D[_x - _sdx][_y - _sdy][0] + (_sdx + _sdy) * prob
                if sc > bestScore:
                    bestScore = sc
                    bestFrom = (fr, _sdx, _sdy)
            #if bestScore >= 0:
            D[_x][_y] = (bestScore, bestFrom)
    # backtrack
    _x = dx
    _y = dy
    aln = []
    #f = open("debug.txt", "a")
    #f.write(structtools.structToStr(D, 2, ""))
    #f.close()
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
    


def main():
    trans = {
        "MM": 0.91,
        "MI": 0.03,
        "MR": 0.03,
        "IM": 0.91,
        "II": 0.03,
        "IR": 0.03,
        "RM": 0.91,
        "RI": 0.03,
        "RR": 0.03,
    }
    
    # Parse input parameters

    sys.argv.append('data/pokus.fa')
    sys.argv.append('data/output.fa')
    alignment_filename = sys.argv[1]
    output_filename = sys.argv[2]

    # Load model
    loader = HMMLoader()
    loader.addDictionary("trans", trans)
    model_filename = "models/repeatHMM.js"
    #model_filename = "models/EditDistanceHMM.js"
    #model_filename = "models/SimpleHMM.js"
    PHMM = loader.load(model_filename)
    
    # Load alignment
    alignment = Fasta.load(alignment_filename)
    if len(alignment) < 2:
        print("ERROR: not enough sequences in file")
        
    # Sequence 1
    seq1 = Fasta.alnToSeq(alignment[0][1])
    seq1_length = len(seq1)
    seq1_name = alignment[0][0]
    
    # Sequence 2
    seq2 = Fasta.alnToSeq(alignment[1][1])
    seq2_length = len(seq2)
    seq2_name = alignment[1][0]
    
    # Compute repeat hints
    for trf_executable in [
                           "/cygdrive/c/cygwin/bin/trf407b.dos.exe",
                           "C:\\cygwin\\bin\\trf407b.dos.exe",
                           "/home/mic/Vyskum/duplikacie/trf404.linux64",
                           ]:
        if os.path.exists(trf_executable):
            trf = TRFDriver(trf_executable)
            break
        
    repeats = trf.run(alignment_filename)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    seq1_repeats = repeats[seq1_name]
    seq2_repeats = repeats[seq2_name]
    PHMM.states[PHMM.statenameToID['Repeat']].addRepeatGenerator(
        RepeatGenerator(seq1_repeats),
        RepeatGenerator(seq2_repeats),
    )
    
    # Compute stuff
    table = PHMM.getPosteriorTable(seq1, 0, seq1_length, seq2, 0, seq2_length)
    alignment = ""
    alignment = realign(
        seq1_name, seq1, 0, seq1_length,
        seq2_name, seq2, 0, seq2_length,
        table,
        PHMM
    )
    
    # Save output
    Fasta.save(alignment, output_filename)
    
    
if __name__ == "__main__":
    main()
    #profile.runctx("""main()""", globals(), locals(), filename='profile.txt')
