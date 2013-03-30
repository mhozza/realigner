import argparse
from tools.file_wrapper import Open
from alignment.Alignment import Alignment
from adapters.TRFDriver import TRFDriver, trf_paths, Repeat
import json
import os
from collections import defaultdict
from alignment import Fasta

def translate_repeat_to_annotation(repeats, seq_to_aln):
    for repeat in repeats:
        repeat.start = seq_to_aln[repeat.start]
        repeat.end = seq_to_aln[repeat.end]
        yield repeat

def toList(s):
    return [s]


def main(inp, out, alignment_regexp, sequence_regexp, trf=trf_paths):
    for trf_executable in trf:
        if os.path.exists(trf_executable):
            trf = TRFDriver(trf_executable, mathType=float)
            break
    repeats = trf.run(inp)

    stats = defaultdict(int)

    for aln in Fasta.load(
        inp,
        alignment_regexp,
        Alignment,
        sequence_selectors=sequence_regexp
    ):
        X_index = 0
        Y_index = 1

        X_trf = list(translate_repeat_to_annotation(
            repeats[aln.names[X_index]], aln.seq_to_aln[X_index]))
        Y_trf = list(translate_repeat_to_annotation(
            repeats[aln.names[Y_index]], aln.seq_to_aln[Y_index]))
        
        X_ann = list("M" * len(aln.sequences[X_index]))
        Y_ann = list("M" * len(aln.sequences[Y_index]))
        B_ann = list("M" * len(aln.sequences[Y_index]))
        for repeat in X_trf:
            if repeat.end >= len(X_ann):
                repeat.end = len(X_ann) - 1
            rlen = 1 + repeat.end - repeat.start
            X_ann[repeat.start : repeat.end + 1] = list("R" * rlen)
            B_ann[repeat.start : repeat.end + 1] = list("R" * rlen)
        for repeat in Y_trf:
            if repeat.end >= len(Y_ann):
                repeat.end = len(Y_ann) - 1
            rlen = 1 + repeat.end - repeat.start
            Y_ann[repeat.start : repeat.end + 1] = list("R" * rlen)
            B_ann[repeat.start : repeat.end + 1] = list("R" * rlen)
        assert(len(X_ann) == len(Y_ann) and len(B_ann) == len(Y_ann))

        M_count = len([x for x in B_ann if x == 'M'])
        R_count = len([x for x in B_ann if x == 'R'])
        R_segments_count = len([x for x in zip('M' + ''.join(B_ann),
                                               ''.join(B_ann) + 'M') 
                                if x[0] != 'R' and x[1] == 'R'])
        stats['M_count'] += M_count
        stats['R_count'] += R_count
        stats['R_segment_count'] += R_segments_count
        changes = [i 
                   for i, x in zip(
                                   range(len(B_ann) + 1), 
                                   zip('M' + ''.join(B_ann),
                                        ''.join(B_ann) + 'M'))
                   if x[0] != x[1]]
        R_segments = [(changes[i], changes[i+1]) 
                      for i in range(0, len(changes) - (len(changes) % 2), 2)]

        assert(R_segments_count == len(R_segments))  
        for start, stop in R_segments:
            XX = 'M'
            YY = 'M'
            for i in range(start, stop):
                if X_ann[i] == 'R':
                    XX = 'R'
                if Y_ann[i] == 'R':
                    YY = 'R'
                assert(B_ann[i] == 'R')
            stats[XX + YY] += 1
        
    with Open(out, 'w') as f:
        json.dump(stats, f, indent=4);


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Compute coverage of ' +
                                     'alignments with repeats.')
    parser.add_argument('input', type=str, help='Input alignment')
    parser.add_argument('output', type=str, help='Output file')
    parser.add_argument('--sequence_regexp', nargs='+', default=None,
                        help='Regular expressions used to select sequences.')
    parser.add_argument('--alignment_regexp', default='', 
                        help='Regular expression used to separate alignment' +
                        'in input file')
    parser.add_argument('--trf', type=toList, default=trf_paths
                        , help="Location of tandem repeat finder binary")

    arg = parser.parse_args()
    main(arg.input, arg.output, arg.alignment_regexp, arg.sequence_regexp, 
         arg.trf)

