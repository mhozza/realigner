#!/usr/bin/python
__author__ = 'michal'

import os
import threading
from hack import transitivitycheck


def realign(src, dest, sX, sY):
    os.system('./mio-test.sh {} {} {} {}'.format(src, dest, sX, sY))


def main():
    src = 'data/sequences/simulated_alignment.fa'
    dst = 'data/sequences/simulated_alignment.{}_{}.realigned.fa'
    sequences = ['sequence1', 'sequence2', 'sequence3']

    threads = list()

    for x in range(len(sequences)-1):
        for y in range(x+1, len(sequences)):
            sX = sequences[x]
            sY = sequences[y]
            if sX != sY:
                dest = dst.format(sX, sY)
                threads.append(
                    threading.Thread(target=realign, args=(src, dest, sX, sY))
                )

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print transitivitycheck.score()

if __name__ == '__main__':
    main()
