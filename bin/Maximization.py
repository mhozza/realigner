# ako vstup dostane model, zoznam súborov a spraví M krok -- každý stav bdue mať
#maximization status
from tools import perf
from tools.file_wrapper import Open
import argparse
from bin.Realign import get_model, getMathType
from collections import defaultdict
import json
from algorithm.LogNum import LogNum

def destroy_lognum(structure):
    t = type(structure)
    if t in [dict, defaultdict]:
        return dict([(k, destroy_lognum(v)) for k, v in structure.iteritems()])
    elif t in [list, tuple]:
        return t([destroy_lognum(v) for v in structure])
    elif t in [type(LogNum())]:
        return float(structure) 
    return structure 

@perf.runningTimeDecorator
def main():
    parser = argparse.ArgumentParser('Compute maximization step.')
    parser.add_argument('--model', type=str, help='Model')
    parser.add_argument('--output', type=str, help='Output file')
    parser.add_argument('--expectations', type=str, help='List of files' + 
                        'containing expectations.', default=[], nargs='+')
    parser.add_argument('--bind_file', nargs='*', help='Replace filenames in '
                        + 'the input_file model.', default=[]) 
    parser.add_argument('--bind_constant', nargs='*', help='Replace constants'
                         + ' in the input_file model.', default=[])
    parser.add_argument('--bind_constant_file', nargs='*', help='Replace' + 
                        ' constants in the input_file model.', default=[])
    parser.add_argument('--mathType', '-m', type=str, default='float',
                        choices=['LogNum', 'float'], help="Numeric type to use")
    args = parser.parse_args()
    args.mathType = getMathType(args.mathType)
    model = get_model(args)
    
    expectations = {
        "transitions": defaultdict(lambda *_: defaultdict(args.mathType)),
        "emissions": [defaultdict(args.mathType)
                      for _ in range(len(model.states))],
    }
    
    # Combine all expectations together ()
    for filename in args.expectations:
        with Open(filename, 'r') as f:
            for exp in json.load(f):
                exp = dict(exp)
                if args.mathType == float:
                    prob = exp['probability']
                else:
                    prob = args.mathType(exp['probability'], False)
                for k, v  in exp['transitions']:
                    x, y = tuple(k)
                    if args.mathType == float:
                        expectations['transitions'][x][y] += prob * v
                    else:
                        expectations['transitions'][x][y] += (
                            prob * args.mathType(v, False))
                for stateID in range(len(exp['emissions'])):
                    for k, v in exp['emissions'][stateID]:
                        k = tuple(k)
                        if args.mathType != float:
                            v = args.mathType(v, False)                            
                        if len(k) == 2:
                            expectations['emissions'][stateID][k] += prob * v
                        else:
                            x, y, cons = k
                            cons = [tuple(_) for _ in cons]
                            if args.mathType == float:
                                cons = [(c, args.mathType(p)) for c, p in cons]
                            else:
                                cons = [(c, args.mathType(p, False)) 
                                        for c, p in cons]
                            if len(cons) == 0:
                                continue
                            total = sum([p for _, p in cons])
                            for c, p in cons:
                                expectations['emissions'][stateID][x, y, c] += (
                                    prob * v * p / total)
                
    # Compute maximization step for transitions (no smoothing)
    for k, v in expectations['transitions'].iteritems():
        total = sum(v.values())
        for kk in v:
            v[kk] /= total
    model.clearTransitions()
    for fromID in range(len(model.states)):
        for toID in range(len(model.states)):
            prob = expectations['transitions'][fromID][toID]
            model.addTransition(fromID, toID, prob)
    # Compute maximization step for emissions (no smoothing)
    for stateID in range(len(model.states)):
        model.states[stateID].trainEmissions(expectations['emissions'][stateID])    
    # Output new model
    json_prep = {"model": destroy_lognum(model.toJSON())}
    with Open(args.output, 'w') as f:
        json.dump(json_prep, f, indent=4)
    return 0 


if __name__ == "__main__":
    ret = main()                                                                                                                                                                               
    perf.printAll()
    exit(ret)
    
