import argparse
import sys

from adapters.TRFDriver import trf_paths
from algorithm.LogNum import LogNum
from alignment.BlockPosteriorRealigner import BlockPosteriorRealigner
from alignment.PosteriorRealigner import PosteriorRealigner
from alignment.ViterbiRealigner import ViterbiRealigner
from hmm.HMMLoader import HMMLoader

def get_math_type(s):
    if s == 'LogNum':
        return LogNum
    elif s == 'float':
        return float
    else:
        raise('Unknown type')
    
    
def toList(s):
    return [s]


def get_realigner(s):
    if s == 'posterior':
        return PosteriorRealigner
    if s == 'block_posterior':
        return BlockPosteriorRealigner        
    elif s == 'viterbi':
        return ViterbiRealigner
    else:
        raise('Unknown type')


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

io_to_dict = lambda x: dict([tuple(y.split(':')) for y in x.split(',')])

# Let's ignore 80 character limit for today
parse_arguments_capabilities_ordered = [
    ('alignment', ([], {'type': str, 'help': 'Input alignment'})),
    ('output_file', ([], {'type': str, 'help': 'Output file'})),
]
parse_arguments_capabilities_keywords = {    
    'mathType': (['-m'],{'type': str, 'default': 'float', 'choices': ['LogNum', 'float'], 'help': 'Numeric type to use'}),
    'model': ([], {'type': str, 'default': 'data/models/repeatHMM.js', 'help': 'Model file'}),
    'trf': ([], {'type': toList, 'default': trf_paths, 'help': 'Location of tandem repeat finder binary'}),
    'algorithm': ([], {'type': str, 'default': 'block_posterior', 'choices': ['posterior', 'block_posterior', 'viterbi'], 'help': 'Which realignment algorithm to use'}),
    'bind_file': ([], {'nargs': '*', 'help': 'Replace filenames in the input_file model.', 'default': []}), 
    'bind_constant': ([], {'nargs': '*', 'help': 'Replace constants in the input_fmodelile model.', 'default': []}),
    'bind_constant_file': ([], {'nargs': '*', 'help': 'Replace constants in the input_file model.', 'default': []}),
    'alignment_regexp': ([], {'default': '', 'help': 'Regular expression used to separate alignment in input file'}),
    'sequence_regexp': ([], {'nargs': '+', 'default': ['sequence1', 'sequence2'],'help': 'Regular expressions used to select sequences.'}),
    'beam_width': ([], {'default': 10, 'type': int, 'help': 'Beam width.'}),
    'repeat_width': ([], {'default': 0, 'help': 'Maximum possible' + ' error of repeat annotation.', 'type': int}),
    'cons_count': ([], {'default': 1, 'help': 'Shift count for repeats.', 'type': int}),
    'tracks': ([], {'help': 'Comma separated list of ' + 'annotation tracks (trf, original_repeats, trf_cons, hmm)', 'type': lambda x: set(x.split(',')), 'default': 'trf'}),
    'intermediate_input_files': ([], {'help': 'Comma separated' + 'list of key value pairs: "key:value". This files ' + 'used to skip load precomputed data in algorithms.', 'type': io_to_dict, 'default': {}}),
    'intermediate_output_files': ([], {'help': 'Comma separated' + 'list of key value pairs: "key:value". This files ' + 'used to skip store precomputed data in algorithms.', 'type': io_to_dict, 'default': {}}),
    'expand_model': ([], {'action': 'store_true'}),
    'marginalize_gaps': ([], {'action': 'store_true'}),
    'one_char_annotation': ([], {'action': 'store_true'}),
    'draw': ([], {'default': '', 'type': str, 'help': 'output file for image'}),
}

def parse_arguments(
    ordered=None,
    keywords=None, 
    description='Realign sequence using informations from tandem repeat finder',
):
    if ordered==None:
        ordered = map(lambda x: x[0], parse_arguments_capabilities_ordered)
    if keywords == None:
        keywords = parse_arguments_capabilities_keywords.keys()
    wat = list()
    temp = dict(parse_arguments_capabilities_ordered)
    for x in ordered:
        wat.append((x, temp[x]))
    for x in keywords:
        wat.append(('--' + x, parse_arguments_capabilities_keywords[x]))
    parser = argparse.ArgumentParser(description)
    for k, (l, dct) in wat:
        k = [k]
        k.extend(l)
        parser.add_argument(*k, **dct)
    parsed_arg = parser.parse_args()
    parsed_arg.mathType = get_math_type(parsed_arg.mathType)
    
    if 'trf_cons' in parsed_arg.tracks:
        parsed_arg.cons_count = 0
    
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
    
    # ====== Load model ========================================================
    parsed_arg.model = get_model(parsed_arg)
    # ====== Get Realigner =====================================================
    parsed_arg.algorithm = get_realigner(parsed_arg.algorithm)
    return parsed_arg
    
