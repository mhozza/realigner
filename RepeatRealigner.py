import AlignmentIterator
from LogNum import LogNum
import sys
from HMMLoader import HMMLoader
from RepeatGenerator import RepeatGenerator
import Fasta
from TRFDriver import TRFDriver

def realign(X_name, X, x, dx, Y_name, Y, y, dy, posteriorTable):
    
    print(posteriorTable)
    
    X_aligned = ""
    Y_aligned = ""
    return {X_name: X_aligned, Y_name: Y_aligned} 
    

if __name__ == "__main__":
    trans = {
        "MM": 0.91,
        "MI": 0.3,
        "MR": 0.3,
        "IM": 0.91,
        "II": 0.3,
        "IR": 0.3,
        "RM": 0.91,
        "RI": 0.3,
        "RR": 0.3,
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
    trf = TRFDriver("C:\\cygwin\\bin\\trf407b.dos.exe")
    repeats = trf.run(alignment_filename)
    seq1_repeats = repeats[seq1_name]
    seq2_repeats = repeats[seq2_name]
    PHMM.states[PHMM.statenameToID['Repeat']].addRepeatGenerator(
        RepeatGenerator(seq1_repeats),
        RepeatGenerator(seq2_repeats),
    )
    
    # Compute stuff
    table = PHMM.getPosteriorTable(seq1, 0, seq1_length, seq2, 0, seq2_length)
    alignment = realign(
        seq1_name, seq1, 0, seq1_length,
        seq2_name, seq2, 0, seq2_length,
        table
    )
    
    # Save output
    Fasta.save(alignment, output_filename)