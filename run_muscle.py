#!/usr/bin/python
__author__ = 'michal'

import os
from alignment.Alignment import Alignment
from alignment import Fasta
from classifier_alignment import transitivitycheck


def select_sequences(inp_filename, out_filename, sequences):
    aln = list(Fasta.load(inp_filename,
                          '',
                          Alignment,
                          sequence_selectors=sequences))[0]
    Fasta.save(zip(aln.names, aln.sequences), out_filename)


def main():
    base_dir = 'data/sequences'
    base_fname = 'simulated_alignment'
    inp_filename = os.path.join(base_dir, base_fname + '.fa')
    tmp_filename = os.path.join(base_dir, base_fname + '.selected.fa')
    out_filename = os.path.join(base_dir, base_fname + '.muscle.fa')
    sequences = ['sequence1', 'sequence2']
    select_sequences(inp_filename, tmp_filename, sequences)
    os.system("muscle -in {inp} -out {out} 2> /dev/null".format(
        inp=tmp_filename,
        out=out_filename,
    ))
    print 'Equality: ' + str(transitivitycheck.compare_with_source(inp_filename, out_filename, sequences[0], sequences[1]))
    os.remove(tmp_filename)

if __name__ == '__main__':
    main()
