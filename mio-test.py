#!/usr/bin/python
__author__ = 'michal'

import os
import threading
import argparse
from classifier_alignment import transitivitycheck


def realign(src, dest, sX, sY, model):
    model_dir = 'data/models'
    os.system(
        './mio-test.sh {} {} {} {} {}'.format(
            src, dest, sX, sY, os.path.join(model_dir, model)
        )
    )


def main(base_filename='simulated_alignment', base_dir='data/sequences'):
    models = ['SimpleHMM.js', 'ClassificationHMM.js', 'OracleHMM.js']
    src = os.path.join(base_dir, base_filename + '.fa')
    # sequences = ['sequence1', 'sequence2', 'sequence3']
    sequences = ['sequence1', 'sequence2']

    for model in models:
        dst = os.path.join(base_dir, base_filename + '.{}_{}.' + model + '.fa')
        threads = list()

        for x in range(len(sequences)-1):
            for y in range(x+1, len(sequences)):
                sX = sequences[x]
                sY = sequences[y]
                if sX != sY:
                    dest = dst.format(sX, sY)
                    threads.append(
                        threading.Thread(target=realign, args=(src, dest, sX, sY, model))
                    )

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        print model
        if len(sequences) == 3:
            print 'Transitivity: ' + str(transitivitycheck.score(dst))
        sX = sequences[0]
        sY = sequences[1]
        print 'Equality: ' + str(transitivitycheck.compare_with_source(src, dst.format(sX, sY), sX, sY))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='name', type=str, default='simulated_alignment', nargs='?')
    parser.add_argument('dir', metavar='dir', type=str, default='data/sequences', nargs='?')
    args = parser.parse_args()
    main(args.name, args.dir)
