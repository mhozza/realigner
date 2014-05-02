#!/usr/bin/python
__author__ = 'michal'

import os
from os import path, listdir
import argparse
from alignment.Alignment import Alignment
from alignment import Fasta
from classifier_alignment import transitivitycheck


def select_sequences(inp_filename, out_filename, sequences):
    aln = list(Fasta.load(inp_filename,
                          '',
                          Alignment,
                          sequence_selectors=sequences))[0]
    Fasta.save(zip(aln.names, aln.sequences), out_filename)


def main(base_fname, base_dir):
    src = os.path.join(base_dir, base_fname)
    tmpf = os.path.join(base_dir, 'realigned/' + base_fname + '.selected.fa')
    dst = os.path.join(
        base_dir, 'realigned/' + os.path.splitext(base_fname)[0] + '.{}_{}.muscle.fa'
    )
    sequences = ['sequence1', 'sequence2', 'sequence3']

    for x in range(len(sequences)-1):
        for y in range(x+1, len(sequences)):
            sX = sequences[x]
            sY = sequences[y]
            if sX != sY:
                select_sequences(src, tmpf, [sequences[x], sequences[y]])
                dest = dst.format(sX, sY)
                os.system("muscle -in {inp} -out {out} 2> /dev/null".format(
                    inp=tmpf,
                    out=dest,
                ))
    if len(sequences) == 3:
        print 'Transitivity: ' + str(transitivitycheck.score(dst))
    sX = sequences[0]
    sY = sequences[1]
    print 'Equality: ' + str(
        transitivitycheck.compare_with_source(src, dst.format(sX, sY), sX, sY)
    )
    os.remove(tmpf)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='name', type=str, default='simulated_alignment', nargs='?')
    parser.add_argument(
        'dir', metavar='dir', type=str, default='data/sequences/simulated', nargs='?'
    )
    parser.add_argument('--multi', action="store_true")
    args = parser.parse_args()
    if args.multi:
        sequences = list()
        for fn in filter(
            lambda x: path.splitext(x)[1] == '.fa' and args.name in path.splitext(x)[0], listdir(args.dir)
        ):
            if path.isfile(path.join(args.dir, fn)):
                main(fn, args.dir)
    else:
        main(args.name+'.fa', args.dir)
