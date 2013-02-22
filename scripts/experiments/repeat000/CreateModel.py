import json
import argparse
from hmm.HMMLoader import HMMLoader  
from tools.my_rand import normalize_dict
import ast
from collections import defaultdict

def main(model_file, additional_parameters,
         emmisions_file, transitions_file, repeat_consensus_file,
         repeat_length_file, repeat_probability, output_file):
    loader = HMMLoader()
    #TODO: prestav konstanty
    for k, v in additional_parameters.iteritems():
        loader.addConstant(k, v)
    
    # Parse emissions
    
    with open(emmisions_file, 'r') as f:
        emm = normalize_dict(json.load(f))
    
    emm = [(ast.literal_eval(k), v) for k, v in emm.iteritems()]
    loader.addConstant('MatchStateEmissions', emm)
    
    background_prob = defaultdict(int)
    for ((r1, r2), v) in emm:
        background_prob[r1] += v
        background_prob[r2] += v
    background_prob = list(normalize_dict(background_prob).iteritems())
    loader.addConstant('background-probability', background_prob)
    
    # Parse transitions
    with open(transitions_file, 'r') as f:
        __trans = normalize_dict(json.load(f))
    trans = dict()
    for k, v in __trans.iteritems():
        trans[''.join(ast.literal_eval(k))] = v * (1 - repeat_probability)
    trans['MI'] *= 0.5
    trans['II'] *= 0.5
    trans['MR'] *= repeat_probability
    trans['IR'] *= repeat_probability
    trans['RR'] *= repeat_probability
    trans['RI'] *= repeat_probability / 6.0
    trans['RM'] *= repeat_probability / 3.0
    loader.addConstant('trans', trans) 
        
    # Parse emissions from trf
    # TODO: relative to consensus output
    loader.addFile('consensus.js', repeat_consensus_file)
    loader.addFile('repeatlength.js', repeat_length_file)
    
    model = loader.load(model_file)
    
    json_prep = {"model": model.toJSON()}
    with open(output_file, 'w') as f:
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
    parser.add_argument('repeat_probability', type=str,
                        help='Probability of repeat in the sequence.')
    parser.add_argument('output', type=str,
                        help='Output file for resulting model')
    parser.add_argument('--parameters', type=str, default='{}',
                        help='Additional parameters (in json as dictionary).')
    parsed_arg = parser.parse_args()
    
    with open(parsed_arg.filenames, 'r') as f:
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