# ako vstup dostane model, zoznam súborov a spraví M krok -- každý stav bdue mať
#maximization status
from tools import perf
from tools.file_wrapper import Open
import argparse
from bin.Realign import get_model, getMathType
from collections import defaultdict
import json



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
                prob = exp.probability
                for k, v  in exp['transitions'].iteritems():
                    x, y = tuple(map(int,k.strip('()').split(',')))
                    expectations['transitions'][x][y] += prob * v
                for stateID in range(len(exp['emissions'].iteritems())):
                    for k, v in exp['emissions'][stateID].iteritems():
                        k = tuple(k[1:len(k) - 1].split(',', 2))
                        if len(k) == 2:
                            expectations['emissions'][stateID][k] += prob * v
                        else:
                            x, y, cons = k
                            cons = [tuple(z.strip('()').split(','))
                                    for z in cons[1:len(cons) - 1].split('),(')]
                            cons = [(c, args.mathType(p)) for c, p in cons]
                            if len(cons) == 0:
                                continue
                            total = sum([p for _, p in cons])
                            for c, p in cons:
                                expectations['emissions'][stateID][x, y, c] = (
                                    prob * p / total)
                
    # Compute maximization step for transitions (no smoothing)
    for k, v in expectations['transitions'].iteritems():
        total = sum(v.values())
        for kk in v:
            v[kk] /= total
    for stateID in range(len(model.states)):
        model.states[stateID].clearTransitions()
    for fromID in range(len(model.states)):
        for toID in range(len(model.states)):
            prob = expectations['transitions'][fromID][toID]
            model.states[fromID].addTransition(toID, prob)
            model.states[toID].addTransition(fromID, prob)
    # Compute maximization step for emissions (no smoothing)
    for stateID in range(len(model.states)):
        model.states[stateID].trainEmissions(expectations['emissions'][stateID])    
    # Output new model
    
    return 0 


if __name__ == "__main__":
    ret = main()                                                                                                                                                                               
    perf.printAll()
    exit(ret)
    