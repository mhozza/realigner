from hmm.HMMLoader import HMMLoader
import argparse
import json
from algorithm.LogNum import LogNum
from collections import defaultdict

def model_to_dot(model):
    
    nodes = []
    edges = []

    for state in model.states:
        em_strs = []
        for k, v in state.emissions.iteritems():
            em_strs.append("""'{}': {:.5}""".format(k, float(v)))
        nodes.append("""
     {name} [
        shape="record"
        label="{emissions}"
     ];
    """.format(name=state.stateName, emissions=' | '.join(em_strs))
    )
    for f, x in model.transitions.iteritems():
        for t, p in model.transitions[f].iteritems():
            edges.append(""" 
            {f} -> {t} [label="{p:.5}"];
            """.format(f=model.states[f].stateName, t=model.states[t].stateName, p=float(p)))
    dot = """digraph {{
    {}
    {}
}}""".format('\n'.join(nodes), '\n'.join(edges))
    return dot;
        

def train(sequences, original_model, new_model):
    loader = HMMLoader(LogNum)
    model = loader.load(original_model)['model']
    with open('mmm.dot', 'w') as f:
        f.write(model_to_dot(model))
    ID = model.statenameToID['Repeat']
    with open(sequences) as f:
        sequences = json.load(f)
    model.states[ID].trainModel(sequences)
    def ln_to_float(x):
        if type(x) in [dict, defaultdict]:
            for k, v in x.iteritems():
                x[k] = ln_to_float(v)
        elif type(x) == list:
            x = map(ln_to_float,x)
        elif type(x) == tuple:
            x = tuple(map(ln_to_float, x))
        elif isinstance(x,LogNum):
            return float(x)
        return x                    
    js = {"model": ln_to_float(model.toJSON())}
    with open(new_model, 'w') as f:
        json.dump(js, f, sort_keys=True, indent=4)
    


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('sequences')
    args.add_argument('original_model')
    args.add_argument('new_model')
    arguments = args.parse_args()
    train(arguments.sequences, arguments.original_model, arguments.new_model)
    
