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
from repeats.RepeatRealignerNoBlocks import RepeatRealignerNoBlocks


def brainwash(className):
    dct = dict();
    for key, value in className.__dict__.iteritems():
        if hasattr(value, '__call__'):
            dct[key] = lambda *_, **__: None
        else: 
            dct[key] = None
    return type('Brainwashed' + className.__name__, (object,), dct)


def get_model(args):
    loader = HMMLoader(args.mathType) # TODO: rename HMMLoader to ModelLoader
    for i in range(0, len(args.bind_file), 2):
        loader.addFile(args.bind_file[i], args.bind_file[i + 1])
    for i in range(0, len(args.bind_constant_file), 2):
        loader.addConstant(
            args.bind_constant_file[i],
            loader.load(args.bind_constant_file[i + 1])
        )
    for i in range(0, len(args.bind_constant_file), 2):
        loader.addConstant(
            args.bind_constant_file[i],
            loader.loads(args.bind_constant_file[i + 1]),
        )
    return loader.load(args.model)["model"]


def compute_annotations(args, alignment_filename):
    annotations = dict()
    if 'trf' in args.tracks:
        trf = None
        for trf_executable in args.trf:
            if os.path.exists(trf_executable):
                trf = TRFDriver(trf_executable, mathType=args.mathType)
                #break
        if trf:
            repeats = trf.run(alignment_filename)
            annotations['trf'] = repeats
                        
    if 'original_repeats' in args.tracks:
        repeats = json.load(Open(alignment_filename + '.repeats',
                                 'r'))
        for k, v in repeats.iteritems():
            repeats[k] = [Repeat(_v[0], _v[1], _v[2], _v[3], _v[4]) 
                          for _v in v]
        
        annotations['original_repeats'] = repeats
            
    perf.msg("Hints computed in {time} seconds.")
    perf.replace()
    return annotations

    
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
    elif s == 'repeat_no_blocks':
        return RepeatRealignerNoBlocks
    else:
        raise('Unknown type')


def parse_arguments():
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
                        default='repeat', choices=['repeat', 'viterbi', 'repeat_no_blocks'],
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
    parser.add_argument('--sequence_regexp', nargs='+', default=["sequence1",
                                                                 "sequence2"],
                        help='Regular expressions used to select sequences.')
    parser.add_argument('--beam_width', default=10, type=int, 
                        help='Beam width.')
    parser.add_argument('--repeat_width', default=0, help='Maximum possible' + 
                        ' error of repeat annotation.', type=int)
    parser.add_argument('--tracks', help='Comma separated list of ' + \
                        'annotation tracks (trf, original_repeats)', 
                        type=lambda x: set(x.split(',')),
                        default='trf')
    io_to_dict = lambda x: dict([tuple(y.split(':')) for y in x.split(',')])
    parser.add_argument('--intermediate_input_files', help='Comma separated' + 
                        'list of key value pairs: "key:value". This files ' + 
                        'used to skip load precomputed data in algorithms.',
                        type=io_to_dict, default={})
    parser.add_argument('--intermediate_output_files', help='Comma separated' + 
                        'list of key value pairs: "key:value". This files ' + 
                        'used to skip store precomputed data in algorithms.',
                        type=io_to_dict, default={},)
    parser.add_argument('--draw', default='', type=str, 
                        help='output file for image')
    parsed_arg = parser.parse_args()
    parsed_arg.mathType = getMathType(parsed_arg.mathType)
    
    # ====== Validate input parameters =========================================
    if len(parsed_arg.bind_file) % 2 != 0:
        sys.stderr.write('ERROR: If binding files, the number of arguments has'
                         + 'to be divisible by 2\n')
        return None 
    if len(parsed_arg.bind_constant_file) % 2 != 0:
        sys.stderr.write('ERROR: If binding constants (as files), the number of'
                         + ' arguments has to be divisible by 2\n')
        return None
    if len(parsed_arg.bind_constant) % 2 != 0:
        sys.stderr.write('ERROR: If binding constants, the number of'
                         + ' arguments has to be divisible by 2\n')
        return None
    return parsed_arg
    

def realign_file(args, model, output_filename, alignment_filename):
    annotations = compute_annotations(args, alignment_filename)
    with Open(output_filename, 'w') as output_file_object:
        for aln in Fasta.load(
            alignment_filename, 
            args.alignment_regexp, 
            Alignment, 
            sequence_selectors=args.sequence_regexp):
            if len(aln.sequences) < 2:
                sys.stderr.write("ERROR: not enough sequences in file\n")
                return 1
            if len(args.draw) == 0:
                drawer = brainwash(AlignmentCanvas)()
            else:
                drawer = AlignmentCanvas()
                drawer.add_original_alignment(aln)
            seq1, seq2 = tuple(map(Fasta.alnToSeq, aln.sequences[:2]))
            perf.msg("Data loaded in {time} seconds.")
            perf.replace()
            realigner = getRealigner(args.algorithm)()
            realigner.prepareData(seq1, aln.names[0], seq2, aln.names[1], aln, 
                                  args.beam_width, drawer, model, args.mathType,
                                  annotations, 
                                  {'input':args.intermediate_input_files,
                                   'output':args.intermediate_output_files},
                                  args.repeat_width)
            aln = realigner.realign(0, len(seq1), 0, len(seq2))
            perf.msg("Sequence was realigned in {time} seconds.")
            perf.replace()
            if len(args.draw) > 0:
                drawer.add_sequence('X', seq1)
                drawer.add_sequence('Y', seq2)
                drawer.add_alignment_line(101, (255, 0, 255, 255), 2, 
                                          AlignmentPositionGenerator(
                                              Alignment([aln[0], aln[2]])))
                drawer.draw(args.draw, 2000, 2000)
                perf.msg("Image was drawn in {time} seconds.")
            # Save output_file
            Fasta.saveAlignmentPiece(aln, output_file_object)


#TODO: if sampling, the alignment is not necessary
@perf.runningTimeDecorator
def worker(transformation):
    # ====== Parse parameters ==================================================
    args = parse_arguments()
    if args is None:
        return 1
        
    alignment_filename_template = args.alignment
    output_filename_template = args.output_file
    
    # ====== Check SGE parameters ==============================================
    task_ids = [None]
    if os.environ.has_key('SGE_TASK_ID'):
        sge_task_id = int(os.environ['SGE_TASK_ID'])
        if 'SGE_STEP_SIZE' not in os.environ:
            sge_step_size = 1
        else:
            sge_step_size = int(os.environ['SGE_STEP_SIZE'])
        sge_task_last = int(os.environ['SGE_TASK_LAST'])
        task_ids = range(
            sge_task_id,
            min(sge_task_id + sge_step_size, sge_task_last + 1)
        )
    
    # ====== Load model ========================================================
    model = get_model(args)

    # ====== Realign all sequences =============================================
    ret = 0
    for task_id in task_ids:
        if task_id == None:
            output_filename = output_filename_template
            alignment_filename = alignment_filename_template
        else:
            output_filename = output_filename_template.format(id=task_id - 1)
            alignment_filename = \
                alignment_filename_template.format(id=task_id - 1)
         
        ret = max(ret,transformation(args, model, output_filename,
                                     alignment_filename))
    return ret


    
if __name__ == "__main__":
    ret = worker(realign_file)
    perf.printAll()
    exit(ret)
