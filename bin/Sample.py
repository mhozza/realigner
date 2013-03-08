from hmm.HMMLoader import HMMLoader
from alignment import Fasta
from tools import perf
import os   
import argparse
import sys
from tools.file_wrapper import Open
import json
    

@perf.runningTimeDecorator
def main():
    
    parser = argparse.ArgumentParser(description='Sample alignments.')
    parser.add_argument('output_file_template', type=str, 
                        help="Template for output file. Have to contain " + \
                        "string '{id}' as placeholder for sequence number.")
    parser.add_argument('--output_files', type=str, help="File where the " + \
                        'list of output files will be written.', default='-')
    parser.add_argument('--model', type=str,
                        default='data/models/repeatHMM.js', help="Model file")
    parser.add_argument('--bind_file', nargs='*', help='Replace filenames in '
                        + 'the input_file model.', default=[]) 
    parser.add_argument('--bind_constant', nargs='*', help='Replace constants'
                         + ' in the input_file model.', default=[])
    parser.add_argument('--bind_constant_file', nargs='*', help='Replace' + 
                        ' constants in the input_file model.', default=[])
    parser.add_argument('n_samples', type=int, help='Number of samples.')
    parser.add_argument('seq1_length',type=int, 
                        help='Length of first sequence.')
    parser.add_argument('seq2_length', type=int, 
                        help='Length of second sequence.')
    parsed_arg = parser.parse_args()
      
    # ====== Validate input parameters =========================================
    print parsed_arg.output_file_template.count("{id}")
    if parsed_arg.output_file_template.count("{id}") < 1:
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
        
    output_filename = parsed_arg.output_file_template
    output_files_filename = parsed_arg.output_files
    output_files = list()
    
    # ====== Load model ========================================================
    loader = HMMLoader() 
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
    PHMM.buildSampleTransitions()
    n_samples = parsed_arg.n_samples
    X_len = parsed_arg.seq1_length
    Y_len = parsed_arg.seq2_length
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
        Fasta.save(aln, output_filename.format(id=i))
        output_files.append(output_filename.format(id=i))
    json.dump(output_files, Open(output_files_filename, 'w'), indent=4)  
    return 0


if __name__ == "__main__":
    ret = main()
    perf.printAll()
    exit(ret)