#!/usr/bin/python
import make_sequence
import argparse
from random import sample


def load_file(fname):
    seq_pairs = []
    with open(fname, 'r') as f:
        state = 0
        for i, line in enumerate(f):
            if len(line) == 0 or line[0] == '#':
                continue
            if state == 0:
                if '0' <= line[0] <= '9':
                    state = 1
                    continue
                else:
                    continue
            if state == 1:
                seq1 = line
                state = 2
                continue
            if state == 2:
                seq_pairs.append((seq1, line))
                state = 0
                continue
    return seq_pairs


def sample_seq(n, seq_list, file_prefix):
    for i, s in enumerate(sample(seq_list, n)):
        make_sequence.main(s, file_prefix + str(i))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', metavar='fname', type=str)
    parser.add_argument('n', metavar='N', type=int)
    args = parser.parse_args()
    seq = load_file(args.fname)
    sample_seq(args.n, seq, 'bio')
