#!/usr/bin/pypy
__author__ = 'michal'

from hack.DataLoader import DataLoader


def create_transitive_alignemnt(p1, p2):
    i = 0
    j = 0
    a = ''
    c = ''
    while i < len(p1[1]) and j < len(p2[0]):
        b1 = p1[0][i]
        b2 = p2[0][j]

        if b1 == b2:
            a += p1[1][i]
            c += p2[1][j]
            i += 1
            j += 1
        elif b1 == '-':
            a += p1[1][i]
            c += '-'
            i += 1
        else:
            a += '-'
            c += p2[1][j]
            j += 1
    print p1[1]
    print p1[0]

    print p2[0]
    print p2[1]

    return a, c


def compare(p1, p2):
    print p1[0]
    print p1[1]
    print p2[1]
    print p2[0]
    s = abs(len(p1[0]) - len(p2[0]))
    for i in range(min(len(p1[0]), len(p2[0]))):
        if p1[0][i] != p2[0][i] or p1[1][i] != p2[1][i]:
            s += 1
    return 1 - float(s) / max(len(p1[0]), len(p2[0]))


def score():
    sequence_names = ['sequence1', 'sequence2', 'sequence3']
    sequences = []

    d = DataLoader()
    for x in range(len(sequence_names)-1):
        for y in range(x+1, len(sequence_names)):
            sX = sequence_names[x]
            sY = sequence_names[y]
            if sX != sY:
                sequences.append(d.getSequences(
                    'data/sequences/simulated_alignment.{}_{}.realigned.fa'.format(
                        sX, sY), [sX+'$', sY+'$']
                    )
                )

    return compare(create_transitive_alignemnt(sequences[0], sequences[1]), sequences[2])

if __name__ == '__main__':
    print score()
