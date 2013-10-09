import argparse
from bin.compareAlignment import main as Compare
from bin.AggregateNumericData import main as Aggregate
from tools import perf


@perf.runningTimeDecorator
def main(correct, aln, part_output, output, types, interval, ignore):
    if types == None:   
        types = [None]
    if not isinstance(types, list):
        raise 'Types have weird type.'
    for tp in types:
        Compare(
            correct.format(id='{id}', type=tp),
            aln.format(id='{id}', type=tp),
            part_output.format(id='{id}', type=tp),
            interval,
        )
        Aggregate(
            [part_output.format(id='{id}', type=tp)],
            output.format(type=tp),
            interval,
            ignore,
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Get results from experiments.')
    parser.add_argument('--correct', required=True, type=str, help='Correct alignment template.')
    parser.add_argument('--aln', required=True, type=str, help='Alignment template.')
    parser.add_argument('--part_output', required=True, type=str, help='Output template for one sequence.')
    parser.add_argument('--types', nargs='*', type=str, help='List of types.')
    parser.add_argument('--interval', nargs=2, type=int, default=None, help='Interval for alignment ids.')
    parser.add_argument('--output', type=str, required=True, help='Output template for one type.')
    parser.add_argument('--ignore', type=str, default='')
    args = parser.parse_args()
    args.ignore = set(map(int, args.ignore.split(',')))
    main(args.correct, args.aln, args.part_output, args.output, args.types, args.interval, args.ignore)
    perf.printAll()
