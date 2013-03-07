import json
import argparse
from hmm.HMMLoader import HMMLoader  
from tools.my_rand import normalize_dict, normalize_tuple_dict
import ast
from collections import defaultdict
import os
from tools.file_wrapper import Open


def main(model_file, additional_parameters,
         emmisions_file, transitions_file, repeat_consensus_file,
         repeat_length_file, repeat_probability, output_file):
    loader = HMMLoader()
    #TODO: prestav konstanty
    for k, v in additional_parameters.iteritems():
        loader.addDictionary(k, v)
    
    # Parse emissions
    
    with Open(emmisions_file, 'r') as f:
        emm = normalize_dict(json.load(f))

    emm = [(ast.literal_eval(k), v) for k, v in emm.iteritems()]
    loader.addDictionary('MatchStateEmissions', {'value': emm})
    
    background_prob = defaultdict(int)
    for ((r1, r2), v) in emm:
        background_prob[r1] += v
        background_prob[r2] += v
    background_prob = \
        {'value': list(normalize_dict(background_prob).iteritems())}
    loader.addDictionary('background-probability', background_prob)
    
    # Parse transitions
    with Open(transitions_file, 'r') as f:
        __trans = json.load(f)
    trans = dict()
    for k, v in __trans.iteritems():
        trans[''.join(ast.literal_eval(k))] = v
    trans = normalize_tuple_dict(trans)
    for k in trans:
        trans[k] *= (1 - repeat_probability)
    trans['MR'] = repeat_probability
    trans['XR'] = repeat_probability
    trans['YR'] = repeat_probability
    trans['RR'] = repeat_probability
    trans['RX'] = (1 - repeat_probability) / 3
    trans['RY'] = (1 - repeat_probability) / 3
    trans['RM'] = (1 - repeat_probability) / 3
       
    loader.addDictionary('trans', trans) 
        
    # Parse emissions from trf
    # TODO: relative to consensus output
    #print os.path.relpath(os.path.abspath(repeat_consensus_file), os.path.dirname(model_file))
    loader.addFile('consensus.js', 
                   os.path.relpath(os.path.abspath(repeat_consensus_file), 
                                   os.path.dirname(model_file)))
    loader.addFile('repeatlength.js', os.path.abspath(repeat_length_file))

    model = loader.load(model_file)
    
    json_prep = {'model': model['model'].toJSON()}
    with Open(output_file, 'w') as f:
        json.dump(json_prep, f, indent=4)
    return output_file


if __name__ == "__main__":    
    #TODO: PARAMETERS
    parser = \
        argparse.ArgumentParser(description='Create specific model from stats')
    parser.add_argument('model', type=str,
                        help='File containing the seleton of the model')
    parser.add_argument('filenames', type=str,
                        help='File containing needed list of files (json' + 
                        ' containing name of files for emissions,' + 
                        ' transition, and statistics from TRF')
    parser.add_argument('repeat_probability', type=float,
                        help='Probability of repeat in the sequence.')
    parser.add_argument('output', type=str,
                        help='Output file for resulting model')
    parser.add_argument('--parameters', type=str, default='{}',
                        help='Additional parameters (in json as dictionary).')
    parsed_arg = parser.parse_args()
    
    with Open(parsed_arg.filenames, 'r') as f:
        files = dict([(x.split('.')[-2], x) for x in json.load(f)])
    main(
         parsed_arg.model,
         json.loads(parsed_arg.parameters),
         files['emission'],
         files['transition'],
         files['trf_consensus'],
         files['trf_length'],
         parsed_arg.repeat_probability,
         parsed_arg.output
    )