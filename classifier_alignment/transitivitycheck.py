#!/usr/bin/pypy
__author__ = 'michal'

from classifier_alignment.DataLoader import DataLoader


def create_alignemnt_function(p):
    l = []
    i0 = 0
    i1 = 0
    j0 = 0
    j1 = 0
    while i0 < len(p[0]) and i1 < len(p[1]):
        l.append((j0, j1))
        if p[0][i0] != '-':
            j0 += 1
        if p[1][i1] != '-':
            j1 += 1
        i0 += 1
        i1 += 1

    def f(ind):
        l2 = set()
        if type(ind) is not list:
            ind = [ind]

        for i in ind:
            l2 |= set(filter(lambda x: x[0] == i, l))
        return map(lambda x: x[1], l2)
    return f


def compare(p1, p2, p3):
    bs = p1[0]
    bs.replace('-', '')
    f1 = create_alignemnt_function(p1)
    f2 = create_alignemnt_function(p2)
    f3 = create_alignemnt_function(p3)

    s = 0
    for i in range(len(bs)):
        if f3(f1(i)) == f2(i):
            s += 1

    return float(s)/len(bs)


def score():
    sequence_names = ['sequence1', 'sequence2', 'sequence3']
    sequences = []
    fname = 'data/sequences/simulated_alignment.{}_{}.realigned.fa'

    d = DataLoader()
    for x in range(len(sequence_names)-1):
        for y in range(x+1, len(sequence_names)):
            sX = sequence_names[x]
            sY = sequence_names[y]
            if sX != sY:
                sequences.append(d.getSequences(
                    fname.format(sX, sY), [sX+'$', sY+'$'])
                )

    return compare(*sequences)

if __name__ == '__main__':
    print score()
