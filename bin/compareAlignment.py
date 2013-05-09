import json
from alignment import Fasta
import argparse
from collections import defaultdict
from tools.file_wrapper import Open
from alignment.Alignment import Alignment
from tools import perf
import os


def expand_repeats(coords, alignment):
    i = 0
    out = []
    while i < len(alignment.sequences[1]):
        if alignment.sequences[1][i] != 'R':
            out.append(coords[i])
        else:
            sets = [set(), set()]
            while (i < len(alignment.sequences[1]) and 
                   alignment.sequences[1][i] == 'R'):
                sets[0].add(coords[i][0])
                sets[1].add(coords[i][2])
                i += 1
            for x in sets[0]:
                for y in sets[1]:
                    out.append((x, -1, y))                    
        i+= 1
    return out


identity = lambda x, *_: x


@perf.runningTimeDecorator
def main(correct_file, aln_file, output_file, interval=None):
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
    if interval != None:
        task_ids = range(interval[0], interval[1] + 1)
    for task_id in task_ids:
        separator = ''
        output = {}
        for fun, tp in [(identity, 'standard'), (expand_repeats, 'expanded_repeats')]:
            for correct, alignment in zip(
                Fasta.load(correct_file.format(id=task_id - 1), separator, Alignment),
                Fasta.load(aln_file.format(id=task_id - 1), separator, Alignment)
            ):
                correct_len = len(correct.getCoordPairs(False))
                ccc = fun(correct.getCoordPairs(False), correct)
                acc = alignment.getCoordPairs(False)
                cc = map(lambda x: (x[0], x[2]), ccc)
                ac = map(lambda x: (x[0], x[2]), acc)
                c = set(cc)
                a = set(ac)
                
                intersect = c.intersection(a)
                not_in_c = c.difference(a)
                not_in_a = a.difference(c)
                symm_diff = c.symmetric_difference(a)
                
                # Find long segments that are correctly aligned
                cseg = [1 if x in c else 0 for x in ac]
                seg_len = []
                length = 0
                segment_length_histogram = defaultdict(int)
                for x in cseg:
                    if x == 0 and length != 0:
                        segment_length_histogram[length] += 1
                    length = length * x + x
                    seg_len.append(length)
                if length > 0:
                    segment_length_histogram[length] += 1
                
                output[tp] = {
                    'corect': correct_file,
                    'alignment': aln_file,
                    'c-lenght': len(cc),
                    'a-length': len(ac),
                    'intersect': len(intersect),
                    '%correct': float(len(intersect) * 100) / correct_len,
                    'c-a': len(not_in_c),
                    'a-c': len(not_in_a),
                    'symmetric_difference': len(symm_diff),
                    'correct_len_histogram': segment_length_histogram
                }
                    
        with Open(output_file.format(id=task_id - 1), 'w') as f:
            json.dump(output, f, indent=4)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze alignment.')
    parser.add_argument('correct', type=str, help='Correct alignment')
    parser.add_argument('aln', type=str, help='Alignment to analyze')
    parser.add_argument('output_file', type=str, help='Output file')
    parser.add_argument('--interval', type=int, nargs=2, default=None,
                        help='Interval of ids (overide SGE settings');
    parsed_arg = parser.parse_args()
    main(parsed_arg.correct, parsed_arg.aln, parsed_arg.output_file,
         parsed_arg.interval)
    perf.printAll() 
