import json
import argparse
from tools.file_wrapper import Open
from tools import perf
import math

def add_dictionaries(dest, src):
    for k, v in src.iteritems():
        # ignore string
        default = None
        if type(v) == int or type(v) == float:
            default = []
        elif isinstance(v, dict):
            default = {}
        else:
            continue
        if k not in dest:
            dest[k] = default
        if isinstance(v, dict):
            add_dictionaries(dest[k], v)
        else:
            dest[k].append(v)


def stats(v):
    total = float(sum(v))
    mean = total / len(v)
    variance = sum([(mean - x)**2 for x in v]) / len(v)
    return (mean, math.sqrt(variance), len(v))


def compute_stats(d):
    for k, v in d.iteritems():
        if k[0] == '+':
            d[k] = sum(v)
        elif isinstance(v, list):
            d[k] = stats(v)
        else:
            if k == 'correct_len_histogram' or k[:2] == '@+':
                for kk, vv in v.iteritems():
                    d[k][kk] = sum(vv)
            else:
                compute_stats(v)


@perf.runningTimeDecorator
def main(args_input, args_output, interval, ignore):
    aggr = dict()
    for task_id in range(interval[0] - 1, interval[1]):
        if task_id == 68 and filename.count('0002')>0:
            print 'removing task_id 68'
            continue
        if task_id in ignore:
            print 'removing task {}'.format(task_id)
            continue
        for filename in args_input:
            with Open(filename.format(id=task_id), 'r') as f:
                data = json.load(f)
                add_dictionaries(aggr, data)
    compute_stats(aggr)
    json.dump(aggr, Open(args_output, 'w'), indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Agregate statistics')
    parser.add_argument('--output', type=str, help='Output file', required=True)
    parser.add_argument('--input', type=str, nargs='+', help='Input files', required=True)
    parser.add_argument('--interval', type=int, nargs=2, 
                        help='Interval of ids for input files', default=None)
    parser.add_argument('--ignore', type=str, default='')
    args = parser.parse_args()
    args.ignore = set(map(int,args.ignore.split(',')))
    main(args.input, args.output, args.interval, args.ignore)
    perf.printAll()
