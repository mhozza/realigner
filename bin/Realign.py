from algorithm.LogNum import LogNum
from hmm.HMMLoader import HMMLoader
from alignment import Fasta
from adapters.TRFDriver import TRFDriver, trf_paths
from alignment.AlignmentIterator import AlignmentBeamGenerator
from repeats.RepeatRealigner import RepeatRealigner
from tools import perf
import os   
import argparse
import sys
from alignment.Alignment import Alignment
from tools.file_wrapper import Open
    
def getMathType(s):
    if s == 'LogNum':
        return LogNum
    elif s == 'float':
        return float
    else:
        raise('Unknown type')
    
    
def toList(s):
    return [s]


def getRealigner(s):
    if s == 'repeat':
        return RepeatRealigner
    else:
        raise('Unknown type')

#TODO: if sampling, the alignment is not necessary
@perf.runningTimeDecorator
def main():
    
    parser = argparse.ArgumentParser(description='Realign sequence using ' + 
                                     'informations from tandem repeat finder')
    parser.add_argument('--mathType', '-m', type=str, default='float',
                        choices=['LogNum', 'float'], help="Numeric type to use")
    parser.add_argument('alignment', type=str, help="Input alignment")
    parser.add_argument('output_file', type=str, help="Output file")
    parser.add_argument('--model', type=str,
                        default='data/models/repeatHMM.js', help="Model file")
    parser.add_argument('--trf', type=toList, default=trf_paths
                        , help="Location of tandem repeat finder binary")
    parser.add_argument('--algorithm', type=str, 
                        default='repeat', choices=['repeat'],
                        help="Which realignment algorithm to use")
    parser.add_argument('--bind_file', nargs='*', help='Replace filenames in '
                        + 'the input_file model.', default=[]) 
    parser.add_argument('--bind_constant', nargs='*', help='Replace constants'
                         + ' in the input_file model.', default=[])
    parser.add_argument('--bind_constant_file', nargs='*', help='Replace' + 
                        ' constants in the input_file model.', default=[])
    parser.add_argument('--sample', nargs=3, default=[], type=int, 
                        required=False, metavar=("n-samples", "X-length", 
                                                 "Y-length"),
                        help="Sample sequences instead of aligning sequences")
    parser.add_argument('--alignment_regexp', default='[.][0-9]+$', 
                        help="Regular expression used to separate alignment" +
                        'in input file')
    parsed_arg = parser.parse_args()
    mathType = getMathType(parsed_arg.mathType)
      
    # ====== Validate input parameters =========================================
    if len(parsed_arg.sample) > 0 and parsed_arg.output_file.count("%d") != 1:
        sys.stderr.write('ERROR: If sampling, output_file filename has to ' +\
                         'contain at least one "%d".\n')
        return 1
    if len(parsed_arg.bind_file) % 2 != 0:
        sys.stderr.write('ERROR: If binding files, the number of arguments has'
                         + 'to be divisible by 2\n')
        return 1 
    if len(parsed_arg.bind_constant_file) % 2 != 0:
        sys.stderr.write('ERROR: If binding constants (as files), the number of'
                         + ' arguments has to be divisible by 2\n')
        return 1
    if len(parsed_arg.bind_constant) % 2 != 0:
        sys.stderr.write('ERROR: If binding constants, the number of'
                         + ' arguments has to be divisible by 2\n')
        return 1
    
    # ====== Parse parameters ==================================================
        
    alignment_filename = parsed_arg.alignment
    output_filename = parsed_arg.output_file
    
    # ====== Load model ========================================================
    loader = HMMLoader(mathType) 
    for i in range(0, len(parsed_arg.bind_constant), 2):
        loader.addFile(parsed_arg.bind_file[i], parsed_arg.bind_file[i + 1])
    for i in range(0, len(parsed_arg.bind_constant_file), 2):
        loader.addConstant(
            parsed_arg.bind_constant_file[i],
            loader.load(parsed_arg.bind_constant_file[i + 1])
        )
    for i in range(0, len(parsed_arg.bind_constant), 2):
        loader.addConstant(
            parsed_arg.bind_constant[i],
            loader.loads(parsed_arg.bind_constant[i + 1]),
        )
    model_filename = parsed_arg.model
    PHMM = loader.load(model_filename)["model"]

    # ====== Sample ============================================================
    if len(parsed_arg.sample) != 0:
        # We are sampling! WOHOOOOO
        PHMM.buildSampleTransitions()
        n_samples, X_len, Y_len = tuple(parsed_arg.sample)
        dirname = os.path.dirname(output_filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        for i in range(n_samples):
            seq = PHMM.generateSequence((X_len, Y_len))
            X = ""
            Y = ""
            A = ""
            for (seq, state) in seq:
                x, y = seq
                dx, dy = len(x), len(y)
                A += PHMM.states[state].getChar() * max(dx, dy)
                X += x + ('-' * (dy - dx))
                Y += y + ('-' * (dx - dy))
            aln = [("sequence1", X), ("alignment", A), ("sequence2", Y)]
            Fasta.save(aln, output_filename % i)  
        return 0
    
    # ====== Load alignment ====================================================
    with Open(output_filename, 'r') as output_file_object:
        for aln in Fasta.load(
            alignment_filename,
            parsed_arg.alignment_regexp,
            Alignment,
        ):
        
            if len(aln.sequences) < 2:
                sys.stderr.write("ERROR: not enough sequences in file\n")
                exit(1)
                
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
            
            #TODO: some better way how to cope with additional information
            # Compute repeat hints
            for trf_executable in parsed_arg.trf:
                if os.path.exists(trf_executable):
                    trf = TRFDriver(trf_executable, mathType=mathType)
                    break
                
            repeats = trf.run(alignment_filename)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
            seq1_repeats = repeats[seq1_name]
            seq2_repeats = repeats[seq2_name]
            
            realigner = getRealigner(parsed_arg.algorithm)()
            realigner.prepareData(PHMM, seq1_repeats, seq2_repeats)
            
            # positions
            positionGenerator = \
                list(AlignmentBeamGenerator(aln, width = 10))
            
            perf.msg("Hints computed in {time} seconds.")
            perf.replace()
            
            # Compute stuff
            table = PHMM.getPosteriorTable(seq1, 0, seq1_length, seq2, 0, seq2_length,
                                           positionGenerator = positionGenerator)
            
            perf.msg("Posterior table computed in {time} seconds.")
            perf.replace()
            
            aln = ""
            aln = realigner.realign(
                seq1_name, seq1, 0, seq1_length,
                seq2_name, seq2, 0, seq2_length,
                table,
                PHMM,
                positionGenerator,
                mathType=mathType
            )
            
            perf.msg("Sequence was realigned in {time} seconds.")
            perf.replace()
            
            # Save output_file
            Fasta.saveAlignmentPiece(aln, output_file_object)

    
if __name__ == "__main__":
    ret = main()
    perf.printAll()
    exit(ret)
    