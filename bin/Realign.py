from algorithm.LogNum import LogNum
from hmm.HMMLoader import HMMLoader
from alignment import Fasta
from adapters.TRFDriver import TRFDriver, trf_paths, Repeat
from alignment.AlignmentIterator import AlignmentPositionGenerator
from repeats.RepeatRealigner import RepeatRealigner
from tools import perf
import os   
import argparse
import sys
from alignment.Alignment import Alignment
from tools.file_wrapper import Open
from alignment.AlignmentCanvas import AlignmentCanvas
import json
from alignment.ViterbiRealigner import ViterbiRealigner


def brainwash(className):
    dct = dict();
    for key, value in className.__dict__.iteritems():
        dct[key] = lambda *_, **__: None
    return type('Lobotomized' + className.__name__, (object,), dct)


def alignment_column_to_annotation(column):
    column = tuple([x if x == '-' else 'M' for x in column])
    if column == ('-', 'M'):
        return 'Y'
    elif column == ('M', '-'):
        return 'X'
    elif column == ('M', 'M'):
        return 'M'
    else:
        return '-'

    
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
    elif s == 'viterbi':
        return ViterbiRealigner
    else:
        raise('Unknown type')

#TODO: if sampling, the alignment is not necessary
@perf.runningTimeDecorator
def main(filename_subst=None):
    
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
                        default='repeat', choices=['repeat', 'viterbi'],
                        help="Which realignment algorithm to use")
    parser.add_argument('--bind_file', nargs='*', help='Replace filenames in '
                        + 'the input_file model.', default=[]) 
    parser.add_argument('--bind_constant', nargs='*', help='Replace constants'
                         + ' in the input_file model.', default=[])
    parser.add_argument('--bind_constant_file', nargs='*', help='Replace' + 
                        ' constants in the input_file model.', default=[])
    parser.add_argument('--alignment_regexp', default='', 
                        help='Regular expression used to separate alignment' +
                        'in input file')
    parser.add_argument('--sequence_regexp', nargs='+', default=None,
                        help='Regular expressions used to select sequences.')
    parser.add_argument('--beam_width', default=10, type=int, 
                        help='Beam width.')
    parser.add_argument('--repeat_width', default=0, help='Maximum possible' + 
                        ' error of repeat annotation.', type=int)
    parser.add_argument('--tracks', help='Comma separated list of ' + \
                        'annotation tracks (trf, original_repeats)', type=str,
                        default='trf')
    parser.add_argument('--intermediate_input_files', help='Comma separated' + 
                        'list of key value pairs: "key:value". This files ' + 
                        'used to skip load precomputed data in algorithms.' )
    parser.add_argument('--intermediate_output_files', help='Comma separated' + 
                        'list of key value pairs: "key:value". This files ' + 
                        'used to skip store precomputed data in algorithms.' )
    parser.add_argument('--draw', default='', type=str, help='output file for image')
    parsed_arg = parser.parse_args()
    mathType = getMathType(parsed_arg.mathType)
    annotations = dict()
    tracks = set(parsed_arg.tracks.split(','))
    io_files = dict();
    if parsed_arg.intermediate_input_files != None:
        io_files['input'] = dict([
            tuple(x.split(':')) 
            for x in parsed_arg.intermediate_input_files.split(',')
        ])
    else:
        io_files['input'] = dict()
    if parsed_arg.intermediate_output_files != None:
        io_files['output'] = dict([
            tuple(x.split(':')) 
            for x in parsed_arg.intermediate_output_files.split(',')
        ])
    else:
        io_files['output'] = dict()

    # ====== Validate input parameters =========================================
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
        
    alignment_filename_template = parsed_arg.alignment
    output_filename_template = parsed_arg.output_file
    
    # ====== Load model ========================================================
    loader = HMMLoader(mathType) # TODO: rename HMMLoader to ModelLoader
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
    model = loader.load(model_filename)["model"]

    # ====== Check SGE parameters ==============================================
    task_ids = [None]
    if os.environ.has_key('SGE_TASK_ID'):
        sge_task_id = int(os.environ['SGE_TASK_ID'])
        sge_step_size = int(os.environ['SGE_STEP_SIZE'])
        sge_task_last = int(os.environ['SGE_TASK_LAST'])
        task_ids = range(
            sge_task_id,
            min(sge_task_id + sge_step_size, sge_task_last + 1)
        )
    for task_id in task_ids:
        if task_id == None:
            output_filename = output_filename_template
            alignment_filename = alignment_filename_template
        else:
            output_filename = output_filename_template.format(id=task_id - 1)
            alignment_filename = \
                alignment_filename_template.format(id=task_id - 1) 
        with Open(output_filename, 'w') as output_file_object:
            for aln in Fasta.load(
                alignment_filename,
                parsed_arg.alignment_regexp,
                Alignment,
                sequence_selectors=parsed_arg.sequence_regexp
            ):
                if len(aln.sequences) < 2:
                    sys.stderr.write("ERROR: not enough sequences in file\n")
                    exit(1)
                    
                if len(parsed_arg.draw) == 0:
                    drawer = brainwash(AlignmentCanvas)()
                else:
                    drawer = AlignmentCanvas()
                # Sequence 1
                seq1 = Fasta.alnToSeq(aln.sequences[0])
                seq1_length = len(seq1)
                seq1_name = aln.names[0]
                drawer.add_sequence('X', seq1)
                
                # Sequence 2
                seq2 = Fasta.alnToSeq(aln.sequences[1])
                seq2_length = len(seq2)
                seq2_name = aln.names[1]
                drawer.add_sequence('Y', seq2)
                
                perf.msg("Data loaded in {time} seconds.")
                perf.replace()
                
                #====== DRAW ORIGINAL ANNOTATION ===============================
                drawer.add_original_alignment(aln) 
                   
                #====== COMPUTE ANNOTATION TRACKS ==============================
                
                # Compute repeat hints
                if 'trf' in tracks:
                    trf = None
                    for trf_executable in parsed_arg.trf:
                        if os.path.exists(trf_executable):
                            trf = TRFDriver(trf_executable, mathType=mathType)
                            break
                    if trf:
                        repeats = trf.run(alignment_filename)
                        annotations['trf'] = repeats
                                    
                if 'original_repeats' in tracks:
                    repeats = json.load(Open(alignment_filename + '.repeats',
                                             'r'))
                    for k, v in repeats.iteritems():
                        repeats[k] = [Repeat(_v[0], _v[1], _v[2], _v[3], _v[4]) 
                                      for _v in v]
                    
                    annotations['original_repeats'] = repeats
                        
                perf.msg("Hints computed in {time} seconds.")
                perf.replace()
        
                #====== REALIGN ================================================
                
                realigner = getRealigner(parsed_arg.algorithm)()
                realigner.prepareData(seq1, seq1_name, seq2, seq2_name, 
                                      aln, parsed_arg.beam_width, drawer, model,
                                      mathType, annotations, io_files, 
                                      parsed_arg.repeat_width)
                aln = realigner.realign(0, seq1_length, 0, seq2_length)

                perf.msg("Sequence was realigned in {time} seconds.")
                perf.replace()

                drawer.add_alignment_line(
                    101,
                    (255, 0, 255, 255),
                    2,
                    AlignmentPositionGenerator(Alignment([aln[0], aln[2]]))
                )
		if len(parsed_arg.draw) > 0:
                    drawer.draw(parsed_arg.draw, 2000, 2000)
		    perf.msg("Image was drawn in {time} seconds.")
                
                # Save output_file
                Fasta.saveAlignmentPiece(aln, output_file_object)

    
if __name__ == "__main__":
    ret = main()
    perf.printAll()
    exit(ret)
    
