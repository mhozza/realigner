__author__ = 'michal'

import os

src = 'data/sequences/simulated_alignment.fa'
sequences = ['sequence1', 'sequence2', 'sequence3']

for x in range(len(sequences)-1):
    for y in range(x+1, len(sequences)):
        sX = sequences[x]
        sY = sequences[y]
        if sX != sY:
            dest = 'data/sequences/' \
                   'simulated_alignment.{}_{}.realigned.fa'.format(sX, sY)
            os.system('./mio-test.sh {} {} {} {}'.format(src, dest, sX, sY))
