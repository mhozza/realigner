import argparse
from alignment.Alignment import Alignment
from alignment import Fasta


def main(arg):
    print arg.output
    with open(arg.output, 'w') as f:
        for alignment_file in arg.alignment:
            alns = Fasta.load(alignment_file, arg.alignment_regexp, Alignment,
                       sequence_selectors=arg.sequence_regexp)
            for aln in alns:
                l = len(aln.sequences[0])
                poss = []
                for i in range(arg.min_split_size, arg.max_split_size + 1):
                    mod = l % i
                    rest = None 
                    if mod >= arg.min_split_size:
                        rest = mod
                    if mod + i <= arg.max_split_size and mod + i >= arg.min_split_size:
                        rest = mod + i
                    if rest == None:
                        continue
                    rest = min(rest, i)
                    poss.append((-rest, i))
                poss.sort()
                _, best = poss[0]
                splits = [i for i in range(0, l, best)]
                if best + l % best < arg.max_split_size:
                    splits.pop()
                splits.append(l)
                for fr, to in zip(splits, splits[1:]):
                    s1 = aln.sequences[0][fr:to]
                    s2 = aln.sequences[1][fr:to]
                    if min(map(len,[s1.strip('-'), s2.strip('-')])) > 0:
                        f.write('{}.{}-{} {}\n'.format(aln.names[0], fr, to, s1))
                        f.write('{}.{}-{} {}\n'.format(aln.names[1], fr, to, s2))
 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split alignment for Context software.')
    parser.add_argument('--alignment', type=str, nargs='+', help='Input alignment')
    parser.add_argument('--output', type=str, help='Output alignment file')
    parser.add_argument('--min_split_size', type=int, default=50, help='Min split size')
    parser.add_argument('--max_split_size', type=int, default=100, help='Max split size')
    parser.add_argument('--alignment_regexp', default='', 
                        help='Regular expression used to separate alignment' +
                        'in input file')
    parser.add_argument('--sequence_regexp', nargs='+', default=["sequence1",
                                                                 "sequence2"],
                        help='Regular expressions used to select sequences.')

    arg = parser.parse_args()
    main(arg)
